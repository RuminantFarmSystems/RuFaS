from dataclasses import replace
import datetime
from math import exp
from typing import Any, Dict, List
from unittest.mock import MagicMock, PropertyMock, call, patch

import pytest
from pytest_mock import MockerFixture

from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.crop_soil_to_feed_storage_connection import HarvestedCrop
from RUFAS.data_structures.manure_supplement_methods import ManureSupplementMethod
from RUFAS.data_structures.manure_to_crop_soil_connection import (
    ManureEventNutrientRequest,
    ManureEventNutrientRequestResults,
)
from RUFAS.data_structures.tillage_implements import TillageImplement
from RUFAS.output_manager import OutputManager
from RUFAS.biophysical.field.crop.crop import Crop
from RUFAS.biophysical.field.crop.crop_data import CropData
from RUFAS.biophysical.field.crop.dormancy import Dormancy
from RUFAS.biophysical.field.crop.harvest_operations import HarvestOperation
from RUFAS.biophysical.field.field.fertilizer_application import FertilizerApplication
from RUFAS.biophysical.field.field.field import Field
from RUFAS.biophysical.field.field.field_data import FieldData
from RUFAS.data_structures.events import (
    BaseFieldManagementEvent,
    FertilizerEvent,
    HarvestEvent,
    ManureEvent,
    PlantingEvent,
    TillageEvent,
)
from RUFAS.biophysical.field.field.manure_application import ManureApplication
from RUFAS.biophysical.field.field.tillage_application import TillageApplication
from RUFAS.biophysical.field.soil.soil import Soil
from RUFAS.biophysical.field.soil.soil_data import SoilData
from RUFAS.data_structures.manure_to_crop_soil_connection import NutrientRequest, NutrientRequestResults
from RUFAS.data_structures.manure_types import ManureType
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits

from tests.test_biophysical.test_crop_soil_field.sample_crop_configuration import SAMPLE_CROP_CONFIGURATION


@pytest.fixture
def mock_crop_data() -> CropData:
    return CropData(**SAMPLE_CROP_CONFIGURATION)


@pytest.fixture
def mock_time() -> RufasTime:
    return MagicMock(auto_spec=RufasTime)


@pytest.fixture
def mock_field_data() -> FieldData:
    return FieldData(
        name="test_field_data",
        field_size=1.5,
    )


def test_field_init_defaults() -> None:
    """Tests that Field initializes correctly with default values when no parameters are provided."""
    # Act
    field = Field()

    # Assert
    assert isinstance(field.om, OutputManager)
    assert isinstance(field.field_data, FieldData)
    assert isinstance(field.soil, Soil)
    assert field.crops == []
    assert field.planting_events == []
    assert field.harvest_events == []
    assert field.fertilizer_events == []
    assert field.tillage_events is None
    assert field.manure_events == []
    assert field.available_fertilizer_mixes == {
        "100_0_0": {"N": 1.0, "P": 0.0, "K": 0.0, "ammonium_fraction": 0.0},
        "26_4_24": {"N": 0.26, "P": 0.04, "K": 0.24, "ammonium_fraction": 0.0},
    }
    assert field.ONLY_NITROGEN_MIX == "100_0_0"
    assert isinstance(field.fertilizer_applicator, FertilizerApplication)
    assert isinstance(field.tiller, TillageApplication)
    assert isinstance(field.manure_applicator, ManureApplication)


def test_manage_field(mocker: MockerFixture) -> None:
    """Tests that all subroutines are correctly called by the main routine in field."""
    field = Field()
    mock_check_fert_app_sched = mocker.patch.object(field, "_check_fertilizer_application_schedule")
    mock_check_tillage_sched = mocker.patch.object(field, "_check_tillage_schedule")
    mock_execute_daily_processes = mocker.patch.object(field, "_execute_daily_processes")
    mock_assess_dormancy = mocker.patch.object(field, "_assess_dormancy")
    mock_check_crop_planting_sched = mocker.patch.object(field, "_check_crop_planting_schedule")
    mock_check_crop_harvest_sched = mocker.patch.object(field, "_check_crop_harvest_schedule")
    mock_remove_dead_crops = mocker.patch.object(field, "_remove_dead_crops")
    mock_execute_manure_application = mocker.patch.object(field, "_execute_manure_application")
    mock_reset_crop_field_coverage_fractions = mocker.patch.object(field, "_reset_crop_field_coverage_fractions")

    mocked_time = MagicMock(RufasTime)
    mocked_weather = MagicMock(CurrentDayConditions)
    setattr(mocked_weather, "daylength", 12)
    setattr(mocked_weather, "rainfall", 3.0)

    manure_event_mock = MagicMock()
    setattr(manure_event_mock, "nitrogen_mass", 10)
    setattr(manure_event_mock, "phosphorus_mass", 5)
    setattr(manure_event_mock, "manure_type", "TypeA")
    setattr(manure_event_mock, "field_coverage", 100)
    setattr(manure_event_mock, "application_depth", 10)
    setattr(manure_event_mock, "surface_remainder_fraction", 0.2)
    setattr(manure_event_mock, "year", 2024)
    setattr(manure_event_mock, "day", 120)
    setattr(manure_event_mock, "manure_supplement_method", ManureSupplementMethod.NONE)

    manure_application_mock = MagicMock(spec=ManureEventNutrientRequestResults)
    manure_application_mock.event = manure_event_mock
    manure_application_mock.nutrient_request_results = "MockResults"
    manure_application_mock.manure_supplement_method = ManureSupplementMethod.NONE

    mock_manure_applications = [manure_application_mock]

    # Act
    field.manage_field(mocked_time, mocked_weather, mock_manure_applications)

    # Assert
    mock_check_fert_app_sched.assert_called_once_with(mocked_time)
    mock_execute_manure_application.assert_called_once_with(
        requested_nitrogen=10,
        requested_phosphorus=5,
        requested_manure_type="TypeA",
        field_coverage=100,
        application_depth=10,
        surface_remainder_fraction=0.2,
        year=2024,
        day=120,
        manure_supplied="MockResults",
        manure_supplement_method=ManureSupplementMethod.NONE,
    )
    mock_check_tillage_sched.assert_called_once_with(mocked_time)
    mock_execute_daily_processes.assert_called_once_with(mocked_weather, mocked_time)
    mock_assess_dormancy.assert_called_once_with(12, 3.0)
    mock_check_crop_planting_sched.assert_called_once_with(mocked_time)
    mock_check_crop_harvest_sched.assert_called_once_with(mocked_time, mocked_weather)
    mock_remove_dead_crops.assert_called_once()
    mock_reset_crop_field_coverage_fractions.assert_called_once()


@pytest.mark.parametrize(
    "all_events,events_remaining,events_occurring_today",
    [
        (
            [
                PlantingEvent("test_1", 1996, 120, False),
                PlantingEvent("test_2", 1996, 120, False),
                PlantingEvent("test_3", 1996, 240, False),
                PlantingEvent("test_4", 1997, 125, False),
            ],
            [
                PlantingEvent("test_3", 1996, 240, False),
                PlantingEvent("test_4", 1997, 125, False),
            ],
            [
                PlantingEvent("test_1", 1996, 120, False),
                PlantingEvent("test_2", 1996, 120, False),
            ],
        ),
        (
            [
                PlantingEvent("crop_1", 1995, 100, True),
                PlantingEvent("crop_2", 1995, 100, False),
                PlantingEvent("crop_3", 1995, 100, False),
            ],
            [],
            [
                PlantingEvent("crop_1", 1995, 100, True),
                PlantingEvent("crop_2", 1995, 100, False),
                PlantingEvent("crop_3", 1995, 100, False),
            ],
        ),
        (
            [
                PlantingEvent("not_today_1", 2000, 100, False),
                PlantingEvent("not_today_2", 2000, 250, True),
                PlantingEvent("not_today_3", 2001, 200, True),
            ],
            [
                PlantingEvent("not_today_1", 2000, 100, False),
                PlantingEvent("not_today_2", 2000, 250, True),
                PlantingEvent("not_today_3", 2001, 200, True),
            ],
            [],
        ),
        ([], [], []),
    ],
)
def test_check_crop_planting_schedule(
    all_events: List[PlantingEvent],
    events_remaining: List[PlantingEvent],
    events_occurring_today: List[PlantingEvent],
) -> None:
    """
    Tests that the planting schedule is updated correctly and that planting events are executed correctly. This test
    contains four cases: some planting events occur on the current day, all planting events occur on the current day,
    no planting events occur on the current day, and no planting events left.
    """
    field = Field(plantings=all_events)
    field._filter_events = MagicMock(return_value=(events_remaining, events_occurring_today))

    field._plant_crop = MagicMock()
    time = MagicMock(RufasTime)
    expected_create_and_update_events_calls = [call(all_events, time)]

    field._check_crop_planting_schedule(time)

    field._filter_events.assert_has_calls(expected_create_and_update_events_calls)
    assert field._plant_crop.call_count == len(events_occurring_today)
    assert field.planting_events == events_remaining


@pytest.mark.parametrize(
    "events,remaining_events,current_events",
    [
        (
            [
                FertilizerEvent(100, 20, "mix_1", 1993, 75, 15, 0, 1.0),
                FertilizerEvent(20, 20, "mix_2", 1993, 75, 15, 0, 1.0),
                FertilizerEvent(15, 15, "mix_3", 1993, 75, 15, 0, 1.0),
            ],
            [],
            [
                FertilizerEvent(100, 20, "mix_1", 1993, 75, 15, 0, 1.0),
                FertilizerEvent(20, 20, "mix_2", 1993, 75, 15, 0, 1.0),
                FertilizerEvent(15, 15, "mix_3", 1993, 75, 15, 0, 1.0),
            ],
        ),
        (
            [
                FertilizerEvent(150, 20, "mix_1", 1992, 80, 15, 0, 1.0),
                FertilizerEvent(25, 5, "mix_1", 1992, 250, 15, 0, 1.0),
                FertilizerEvent(100, 50, "mix_1", 1993, 80, 15, 0, 1.0),
            ],
            [
                FertilizerEvent(25, 5, "mix_1", 1992, 250, 15, 0, 1.0),
                FertilizerEvent(100, 50, "mix_1", 1993, 80, 15, 0, 1.0),
            ],
            [FertilizerEvent(150, 20, "mix_1", 1992, 80, 15, 0, 1.0)],
        ),
        (
            [
                FertilizerEvent(50, 10, "mix_1", 1998, 90, 15, 0, 1.0),
                FertilizerEvent(50, 10, "mix_1", 1999, 90, 15, 0, 1.0),
                FertilizerEvent(50, 10, "mix_1", 2000, 90, 15, 0, 1.0),
            ],
            [
                FertilizerEvent(50, 10, "mix_1", 1998, 90, 15, 0, 1.0),
                FertilizerEvent(50, 10, "mix_1", 1999, 90, 15, 0, 1.0),
                FertilizerEvent(50, 10, "mix_1", 2000, 90, 15, 0, 1.0),
            ],
            [],
        ),
    ],
)
def test_check_fertilizer_application_schedule(
    events: List[FertilizerEvent],
    remaining_events: List[FertilizerEvent],
    current_events: List[FertilizerEvent],
) -> None:
    """Tests that fertilizer events that occur on the current day are properly selected and executed."""
    field = Field(fertilizer_events=events)
    field._filter_events = MagicMock(return_value=(remaining_events, current_events))
    field._execute_fertilizer_application = MagicMock()
    mocked_time = MagicMock(RufasTime)
    setattr(mocked_time, "calendar_year", 2000)
    setattr(mocked_time, "day", 100)

    field._check_fertilizer_application_schedule(mocked_time)

    expected_execution_calls = []
    for event in current_events:
        expected_execution_calls.append(
            call(
                event.mix_name,
                event.nitrogen_mass,
                event.phosphorus_mass,
                event.potassium_mass,
                event.depth,
                event.surface_remainder_fraction,
                event.year,
                event.day,
            )
        )
    field._filter_events.assert_called_once_with(events, mocked_time)
    field._execute_fertilizer_application.assert_has_calls(expected_execution_calls)


def test_check_manure_application_schedule() -> None:
    """Tests that ManureEvents are correctly checked and converted to ManureEventNutrientRequests when scheduled."""

    # Arrange
    manure_events = [
        ManureEvent(
            100,
            20,
            ManureType.LIQUID,
            ManureSupplementMethod.SYNTHETIC_FERTILIZER,
            0.8,
            0.0,
            1.0,
            1991,
            120,
        ),
        ManureEvent(90, 25, ManureType.SOLID, ManureSupplementMethod.SYNTHETIC_FERTILIZER, 0.9, 0.1, 0.9, 1992, 120),
        ManureEvent(
            80, 30, ManureType.LIQUID, ManureSupplementMethod.SYNTHETIC_FERTILIZER, 0.85, 0.05, 0.95, 1991, 121
        ),
    ]
    field = Field(manure_events=manure_events)
    field.field_data = MagicMock()
    field.field_data.name = "field1"

    filtered_manure_events = [manure_events[0], manure_events[1]]
    field._filter_events = MagicMock(return_value=(manure_events[2:], filtered_manure_events))
    field._create_manure_request = MagicMock(side_effect=lambda event: f"Request for {event.year}-{event.day}")
    mocked_time = MagicMock(RufasTime)
    mocked_time.calendar_year = 1991
    mocked_time.day = 120

    # Act
    manure_requests = field.check_manure_application_schedule(mocked_time)

    # Assert
    field._filter_events.assert_called_once_with(manure_events, mocked_time)
    assert field.manure_events == [manure_events[2]], "Expected remaining events after filtering."
    expected_requests = [
        ManureEventNutrientRequest("field1", filtered_manure_events[0], "Request for 1991-120"),
        ManureEventNutrientRequest("field1", filtered_manure_events[1], "Request for 1992-120"),
    ]
    assert manure_requests == expected_requests, "Expected manure requests do not match."
    field._create_manure_request.assert_any_call(filtered_manure_events[0])
    field._create_manure_request.assert_any_call(filtered_manure_events[1])
    assert field._create_manure_request.call_count == len(filtered_manure_events)


def test_check_manure_application_schedule_integration() -> None:
    """Integration test for check_manure_application_schedule()."""
    # Arrange
    field = Field()
    mocked_time = MagicMock(RufasTime)
    setattr(mocked_time, "year", 2024)
    setattr(mocked_time, "day", 120)
    setattr(mocked_time, "current_date", RufasTime.convert_year_jday_to_date(2024, 120))
    manure_event_today = MagicMock()
    setattr(manure_event_today, "year", 2024)
    setattr(manure_event_today, "day", 120)
    setattr(manure_event_today, "nitrogen_mass", 10)
    setattr(manure_event_today, "phosphorus_mass", 5)
    setattr(manure_event_today, "manure_type", ManureType.LIQUID)
    setattr(manure_event_today, "date_occurs", RufasTime.convert_year_jday_to_date(2024, 120).date())
    manure_event_today.occurs_today.return_value = True

    manure_event_other_day = MagicMock()
    setattr(manure_event_other_day, "year", 2024)
    setattr(manure_event_other_day, "day", 121)
    setattr(manure_event_other_day, "date_occurs", RufasTime.convert_year_jday_to_date(2024, 125).date())
    manure_event_other_day.occurs_today.return_value = False

    field.manure_events = [manure_event_today, manure_event_other_day]
    field.om = MagicMock()

    # Act
    manure_requests = field.check_manure_application_schedule(mocked_time)

    # Assert
    assert len(manure_requests) == 1
    assert manure_requests[0].event == manure_event_today
    assert manure_requests[0].nutrient_request.nitrogen == 10
    assert manure_requests[0].nutrient_request.phosphorus == 5
    assert manure_requests[0].nutrient_request.manure_type == ManureType.LIQUID


@pytest.mark.parametrize(
    "nitrogen_mass, phosphorus_mass, manure_type, expected_request, expected_log",
    [
        # Case: Nutrients requested, expect a NutrientRequest and no log
        (
            50.0,
            25.0,
            ManureType.LIQUID,
            NutrientRequest(
                nitrogen=50.0, phosphorus=25.0, manure_type=ManureType.LIQUID, use_supplemental_manure=False
            ),
            None,
        ),
        # Case: No nutrients requested, expect None and a log message
        (0.0, 0.0, ManureType.LIQUID, None, "Tried to apply manure with no nitrogen or phosphorus requested."),
    ],
)
def test_create_manure_request(
    nitrogen_mass: float,
    phosphorus_mass: float,
    manure_type: ManureType,
    expected_request: NutrientRequest | None,
    expected_log: str | None,
) -> None:
    """Tests _create_manure_request for both nutrient-requested and no-nutrient cases."""
    # Arrange
    field = Field()
    field.om = MagicMock()

    manure_event = ManureEvent(
        year=2023,
        day=120,
        nitrogen_mass=nitrogen_mass,
        phosphorus_mass=phosphorus_mass,
        manure_type=manure_type,
        field_coverage=0.9,
        application_depth=0.2,
        surface_remainder_fraction=0.8,
        manure_supplement_method=ManureSupplementMethod.NONE,
    )

    # Act
    nutrient_request = field._create_manure_request(manure_event)

    # Assert
    if expected_request is not None:
        assert nutrient_request is not None
        assert isinstance(nutrient_request, NutrientRequest)
        assert nutrient_request.nitrogen == expected_request.nitrogen
        assert nutrient_request.phosphorus == expected_request.phosphorus
        assert nutrient_request.manure_type == expected_request.manure_type
        field.om.add_warning.assert_not_called()

    else:
        assert nutrient_request is None
        field.om.add_warning.assert_called_once_with(
            "Manure Application Warning",
            expected_log,
            {
                "class": field.__class__.__name__,
                "function": field._create_manure_request.__name__,
                "suffix": f"field='{field.field_data.name}'",
                "year": manure_event.year,
                "day": manure_event.day,
            },
        )


@pytest.mark.parametrize(
    "year,day,all_harvest_events,current_harvest_events,expected_harvest_count",
    [
        (
            1990,
            240,
            [
                HarvestEvent("corn", 1990, 240, "no_kill"),
                HarvestEvent("corn", 1990, 255, "default"),
            ],
            [HarvestEvent("cover", 1990, 240, "default")],
            1,
        ),
        (
            1991,
            126,
            [
                HarvestEvent("corn", 1991, 240, "default"),
                HarvestEvent("cover", 1991, 260, "default"),
            ],
            [],
            0,
        ),
        (
            1992,
            230,
            [
                HarvestEvent("corn", 1992, 230, "default"),
                HarvestEvent("cover_1", 1992, 230, "default"),
                HarvestEvent("cover_2", 1992, 230, "default"),
            ],
            [
                HarvestEvent("corn", 1992, 230, "default"),
                HarvestEvent("cover_1", 1992, 230, "default"),
                HarvestEvent("cover_2", 1992, 230, "default"),
            ],
            3,
        ),
        (1993, 145, [], [], 0),
    ],
)
def test_check_crop_harvest_schedule(
    mocker: MockerFixture,
    year: int,
    day: int,
    all_harvest_events: list[HarvestEvent],
    current_harvest_events: list[HarvestEvent],
    expected_harvest_count: int,
) -> None:
    """Tests that the schedule of crop harvests is determined correctly for any given day."""
    field = Field(harvestings=all_harvest_events)

    mocked_time = MagicMock(RufasTime)
    mocked_time.calendar_year = year
    mocked_time.day = day
    mocked_time.current_date = datetime.datetime(year, 1, 1) + datetime.timedelta(days=day - 1)
    setattr(mocked_time, "calendar_year", year)
    setattr(mocked_time, "day", day)
    mock_conditions = MagicMock(CurrentDayConditions)
    remaining_harvest_events = [events for events in all_harvest_events if events not in current_harvest_events]
    filter_events = mocker.patch.object(
        field, "_filter_events", return_value=(remaining_harvest_events, current_harvest_events)
    )
    mock_harvested_crop = HarvestedCrop(
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
    )
    harvest_crop = mocker.patch.object(field, "_harvest_crop", return_value=[mock_harvested_crop])
    harvest_heat_scheduled = mocker.patch.object(field, "_harvest_heat_scheduled_crops")

    harvest_crop_calls = []
    for event in current_harvest_events:
        new_call = call(event.crop_reference, event.operation, mocked_time, mock_conditions)
        harvest_crop_calls.append(new_call)

    actual = field._check_crop_harvest_schedule(mocked_time, mock_conditions)

    filter_events.assert_called_once_with(all_harvest_events, mocked_time)
    harvest_crop.assert_has_calls(harvest_crop_calls)
    assert len(actual) == expected_harvest_count
    harvest_heat_scheduled.assert_called_once()


@pytest.mark.parametrize(
    "crop_num,should_harvest_results,expected_harvest_count",
    [
        (5, [True, False, True, True, False], 3),
        (2, [True, True], 2),
        (2, [False, False], 0),
        (0, [], 0),
    ],
)
def test_harvest_heat_scheduled_crops(
    mock_time: RufasTime,
    mock_field_data: FieldData,
    crop_num: int,
    should_harvest_results: List[bool],
    expected_harvest_count: int,
) -> None:
    """Tests that all crops which are set to be harvested based on heat level are."""
    crops = []
    for index in range(crop_num):
        mock_crop = MagicMock(Crop)
        mock_crop.should_harvest_based_on_heat.return_value = should_harvest_results[index]
        mock_crop_management = MagicMock()
        mock_crop.crop_management = mock_crop_management
        crops.append(mock_crop)

    field = Field(
        field_data=mock_field_data,
    )
    field.crops = crops
    with patch.object(
        field.soil.carbon_cycling.residue_partition,
        "add_residue_to_pools",
        new_callable=MagicMock,
    ) as add_residue:
        field._harvest_heat_scheduled_crops(10.0, mock_time)

    actual_harvest_count = 0
    for index, crop in enumerate(crops):
        if should_harvest_results[index]:
            crop.manage_crop_harvest.assert_called_once_with(
                HarvestOperation.HARVEST_ONLY,
                mock_field_data.name,
                mock_field_data.field_size,
                mock_time,
                field.soil.data,
            )
            actual_harvest_count += 1
        else:
            crop.manage_crop_harvest.assert_not_called()

    assert add_residue.call_count == expected_harvest_count
    assert actual_harvest_count == expected_harvest_count


@pytest.mark.parametrize(
    "events,year,day,expected_remaining,expected_current",
    [
        (
            [
                BaseFieldManagementEvent(1990, 120),
                BaseFieldManagementEvent(1990, 200),
                BaseFieldManagementEvent(1993, 100),
            ],
            1990,
            120,
            [BaseFieldManagementEvent(1990, 200), BaseFieldManagementEvent(1993, 100)],
            [BaseFieldManagementEvent(1990, 120)],
        ),
        (
            [
                PlantingEvent("corn", False, 1993, 120),
                PlantingEvent("corn_supplement", True, 1993, 120),
                PlantingEvent("cover_crop", False, 1993, 245),
            ],
            1993,
            120,
            [PlantingEvent("cover_crop", False, 1993, 245)],
            [
                PlantingEvent("corn", False, 1993, 120),
                PlantingEvent("corn_supplement", True, 1993, 120),
            ],
        ),
        (
            [
                HarvestEvent(
                    "corn_1",
                    HarvestOperation.HARVEST_KILL,
                    1999,
                    240,
                ),
                HarvestEvent(
                    "corn_1",
                    HarvestOperation.HARVEST_KILL,
                    2000,
                    240,
                ),
                HarvestEvent(
                    "alfalfa_2",
                    HarvestOperation.HARVEST_KILL,
                    2001,
                    240,
                ),
            ],
            1999,
            200,
            [
                HarvestEvent("corn_1", HarvestOperation.HARVEST_KILL, 1999, 240),
                HarvestEvent("corn_1", HarvestOperation.HARVEST_KILL, 2000, 240),
                HarvestEvent("alfalfa_2", HarvestOperation.HARVEST_KILL, 2001, 240),
            ],
            [],
        ),
        ([], 1993, 140, [], []),
    ],
)
def test_filter_events(
    events: List[BaseFieldManagementEvent],
    year: int,
    day: int,
    expected_remaining: List[BaseFieldManagementEvent],
    expected_current: List[BaseFieldManagementEvent],
) -> None:
    """Tests that list of events are properly checked and have current events correctly removed from them."""
    mocked_time = MagicMock(RufasTime)
    setattr(mocked_time, "current_calendar_year", year)
    setattr(mocked_time, "current_julian_day", day)
    setattr(mocked_time, "current_date", RufasTime.convert_year_jday_to_date(year, day))

    actual = Field._filter_events(events, mocked_time)
    assert actual[0] == expected_remaining
    assert actual[1] == expected_current


@pytest.mark.parametrize(
    "crop_reference,heat_scheduled,year,day",
    [
        ("corn_silage", False, 1990, 120),
        ("alien_crop", True, 2000, 110),
    ],
)
def test_plant_crop(
    mocker: MockerFixture,
    mock_crop_data: CropData,
    crop_reference: str,
    heat_scheduled: bool,
    year: int,
    day: int,
) -> None:
    """Tests that a new Crop instance is properly created and added to a field."""
    field_data = FieldData(name="test", field_size=1.3)
    field = Field(field_data=field_data)
    mocked_time = MagicMock(RufasTime)
    setattr(mocked_time, "current_calendar_year", year)
    setattr(mocked_time, "current_julian_day", day)
    mock_crop_data.name = crop_reference
    created_crop = Crop(mock_crop_data)
    mock_create = mocker.patch.object(Crop, "create_crop", return_value=created_crop)
    mock_record = mocker.patch.object(field, "_record_planting")

    field._plant_crop(crop_reference, heat_scheduled, mocked_time)

    assert len(field.crops) == 1  # Ensure one crop is added
    assert field.crops[0] == created_crop
    mock_create.assert_called_once_with(crop_reference, heat_scheduled, mocked_time)
    mock_record.assert_called_once_with(heat_scheduled, crop_reference, year, day)


@pytest.mark.parametrize(
    "heat_scheduled,year,day,field_name,field_size,expected_info_map,expected_value",
    [
        (
            False,
            1993,
            100,
            "name_1",
            1.3,
            {
                "suffix": "field='name_1'",
                "units": {
                    "crop": MeasurementUnits.UNITLESS.value,
                    "heat_scheduled_harvest": MeasurementUnits.UNITLESS.value,
                    "year": MeasurementUnits.CALENDAR_YEAR.value,
                    "day": MeasurementUnits.ORDINAL_DAY.value,
                    "field_size": MeasurementUnits.HECTARE.value,
                    "average_clay_percent": MeasurementUnits.PERCENT.value,
                    "field_name": MeasurementUnits.UNITLESS.value,
                },
            },
            {
                "crop": "corn_grain",
                "heat_scheduled_harvest": False,
                "year": 1993,
                "day": 100,
                "field_size": 1.3,
                "average_clay_percent": 40.0,
                "field_name": "name_1",
            },
        ),
        (
            True,
            1996,
            120,
            "name_2",
            2.55,
            {
                "suffix": "field='name_2'",
                "units": {
                    "crop": MeasurementUnits.UNITLESS.value,
                    "heat_scheduled_harvest": MeasurementUnits.UNITLESS.value,
                    "year": MeasurementUnits.CALENDAR_YEAR.value,
                    "day": MeasurementUnits.ORDINAL_DAY.value,
                    "field_size": MeasurementUnits.HECTARE.value,
                    "average_clay_percent": MeasurementUnits.PERCENT.value,
                    "field_name": MeasurementUnits.UNITLESS.value,
                },
            },
            {
                "crop": "winter_wheat_grain",
                "heat_scheduled_harvest": True,
                "year": 1996,
                "day": 120,
                "field_size": 2.55,
                "average_clay_percent": 40.0,
                "field_name": "name_2",
            },
        ),
        (
            False,
            2008,
            122,
            "name_3",
            0.95,
            {
                "suffix": "field='name_3'",
                "units": {
                    "crop": MeasurementUnits.UNITLESS.value,
                    "heat_scheduled_harvest": MeasurementUnits.UNITLESS.value,
                    "year": MeasurementUnits.CALENDAR_YEAR.value,
                    "day": MeasurementUnits.ORDINAL_DAY.value,
                    "field_size": MeasurementUnits.HECTARE.value,
                    "average_clay_percent": MeasurementUnits.PERCENT.value,
                    "field_name": MeasurementUnits.UNITLESS.value,
                },
            },
            {
                "crop": "soybean_grain",
                "heat_scheduled_harvest": False,
                "year": 2008,
                "day": 122,
                "field_size": 0.95,
                "average_clay_percent": 40.0,
                "field_name": "name_3",
            },
        ),
    ],
)
def test_record_planting(
    heat_scheduled: bool,
    year: int,
    day: int,
    field_name: str,
    field_size: float,
    expected_info_map: dict[str, Any],
    expected_value: dict[str, Any],
) -> None:
    """Tests that crop plantings are correctly recorded to the OutputManager."""
    field = Field(field_data=FieldData(name=field_name, field_size=field_size))
    with patch(
        "RUFAS.biophysical.field.soil.soil_data.SoilData.average_clay_percent",
        new_callable=PropertyMock,
        return_value=40.0,
    ) as clay:
        field._record_planting(heat_scheduled, expected_value["crop"], year, day)

        clay.assert_called_once()
    actual = field.om.variables_pool[f"Field._record_planting.crop_planting.field='{field_name}'"]
    assert actual["info_maps"].__contains__(expected_info_map)
    assert actual["values"].__contains__(expected_value)


@pytest.mark.parametrize(
    "crop_reference,harvest_op,rainfall",
    [
        ("test_1", HarvestOperation.HARVEST_KILL, 0.0),
        ("test_2", HarvestOperation.HARVEST_ONLY, 10.3),
        ("test_3", HarvestOperation.KILL_ONLY, 0.5),
    ],
)
def test_harvest_crop(
    mock_crop_data: CropData,
    mock_time: RufasTime,
    mock_field_data: FieldData,
    crop_reference: str,
    harvest_op: HarvestOperation,
    rainfall: float,
) -> None:
    """Tests that crops are harvested correctly."""
    harvest_crop = Crop(crop_data=mock_crop_data)
    harvest_crop.data.id = crop_reference
    other_crop_1 = Crop(crop_data=replace(mock_crop_data))
    other_crop_2 = Crop(crop_data=replace(mock_crop_data))
    other_crop_1.data.id, other_crop_2.data.id = "not this crop", "not this crop"
    field = Field(
        field_data=mock_field_data,
    )
    field.crops = [harvest_crop, other_crop_1, other_crop_2]
    for crop in field.crops:
        crop.manage_crop_harvest = MagicMock()
    mock_conditions = MagicMock(CurrentDayConditions)
    mock_conditions.rainfall = rainfall

    with patch.object(
        field.soil.carbon_cycling.residue_partition,
        "add_residue_to_pools",
        new_callable=MagicMock,
    ) as add_residue:
        field._harvest_crop(crop_reference, harvest_op, mock_time, mock_conditions)

    for crop in field.crops:
        if crop.data.id == "not this crop":
            crop.manage_crop_harvest.assert_not_called()
        else:
            crop.manage_crop_harvest.assert_called_once_with(
                harvest_op,
                mock_field_data.name,
                mock_field_data.field_size,
                mock_time,
                field.soil.data,
            )
    assert add_residue.call_count == 1


@pytest.mark.parametrize(
    "crop_count,expected_message",
    [
        (2, "Multiple crops to be harvested by single HarvestEvent."),
        (0, "No crop found to be harvested by a HarvestEvent."),
    ],
)
def test_harvest_crop_warnings(
    mock_crop_data: CropData,
    mock_time: RufasTime,
    mock_field_data: FieldData,
    crop_count: int,
    expected_message: str,
) -> None:
    """Tests that warnings are raised correctly to the OutputManager."""
    crops = [Crop(crop_data=mock_crop_data) for _ in range(crop_count)]
    with patch("RUFAS.output_manager.Utility.get_timestamp") as mocked_timestamp:
        timestamp = "00-Jan-1970_Thu_00-00-00"
        expected_info_map = {
            "suffix": f"field='{mock_field_data.name}'",
            "day": mock_time.current_julian_day,
            "year": mock_time.current_calendar_year,
            "timestamp": timestamp,
        }

        for crop in crops:
            crop._data.id = "test"
            crop.manage_crop_harvest = MagicMock()
        field = Field(
            field_data=mock_field_data,
        )
        field.crops = crops
        mocked_timestamp.return_value = timestamp
        mock_conditions = MagicMock(CurrentDayConditions)
        mock_conditions.rainfall = 11.0

        with patch.object(
            field.soil.carbon_cycling.residue_partition,
            "add_residue_to_pools",
            new_callable=MagicMock,
        ) as add_residue:
            field._harvest_crop("test", HarvestOperation.HARVEST_KILL, mock_time, mock_conditions)

        for crop in crops:
            crop.manage_crop_harvest.assert_called_once_with(
                HarvestOperation.HARVEST_KILL,
                mock_field_data.name,
                mock_field_data.field_size,
                mock_time,
                field.soil.data,
            )
        assert add_residue.call_count == len(crops)
        actual = field.om.warnings_pool[f"Field._harvest_crop.harvest_warning.field='{mock_field_data.name}'"]
        assert actual["info_maps"].__contains__(expected_info_map)
        assert actual["values"].__contains__(expected_message)


def test_remove_dead_crops(mock_crop_data: CropData) -> None:
    """
    Tests that dead crops are removed from a field correctly.
    This test contains four cases: there are no crops in the field, some crops in the field are dead, no crops in the
    field are dead, and all crops in the field are dead.
    """
    field_1 = Field()
    field_1._remove_dead_crops()
    assert field_1.crops == []

    field_2 = Field()
    crop_1 = Crop(crop_data=mock_crop_data)
    crop_1._data.is_alive = False
    crop_2 = Crop(crop_data=replace(mock_crop_data))
    crop_3 = Crop(crop_data=replace(mock_crop_data))
    crop_2._data.is_alive, crop_3._data.is_alive = True, True
    field_2.crops = [crop_1, crop_2, crop_3]
    field_2._remove_dead_crops()
    assert field_2.crops == [crop_2, crop_3]

    field_3 = Field()
    mock_crop_data.is_alive = True
    crop_4 = Crop(crop_data=mock_crop_data)
    crop_5 = Crop(crop_data=mock_crop_data)
    crop_6 = Crop(crop_data=mock_crop_data)
    field_3.crops = [crop_4, crop_5, crop_6]
    field_3._remove_dead_crops()
    assert field_3.crops == [crop_4, crop_5, crop_6]

    field_4 = Field()
    crop_7 = Crop(crop_data=mock_crop_data)
    crop_8 = Crop(crop_data=mock_crop_data)
    field_4.crops = [crop_7, crop_8]
    field_4._remove_dead_crops()
    assert field_4.crops == [crop_7, crop_8]


@pytest.mark.parametrize(
    "crop_count,expected_field_proportion",
    [
        (3, (1 / 3)),
        (1, 1.0),
        (4, 0.25),
        (0, None),
    ],
)
def test_reset_crop_field_coverage_fractions(
    mock_crop_data: CropData, crop_count: int, expected_field_proportion: float
) -> None:
    """Tests that crops in a field correctly have their proportion reset when there are other crops present."""
    field = Field()
    crop_list = [Crop(crop_data=mock_crop_data) for _ in range(crop_count)]
    field.crops = crop_list
    field._reset_crop_field_coverage_fractions()
    for crop in field.crops:
        assert crop._data.field_proportion == expected_field_proportion


@pytest.mark.parametrize(
    "daylength,threshold_daylength",
    [
        (14, 8),
        (17.20948239, 9.19183294),
        (7.293485893, 8.234850920),
    ],
)
def test_start_dormancy(mock_crop_data: CropData, daylength: float, threshold_daylength: float) -> None:
    """Tests that each crop's dormancy method is called."""
    crop = Crop(mock_crop_data)
    field = Field()
    field.field_data.dormancy_threshold_daylength = threshold_daylength
    field.crops = [crop]
    rainfall = 10.3

    with (
        patch(
            "RUFAS.biophysical.field.crop.dormancy.Dormancy.enter_dormancy",
            new_callable=MagicMock,
        ) as dormancy,
        patch(
            "RUFAS.biophysical.field.crop.biomass_allocation.BiomassAllocation.partition_biomass",
            new_callable=MagicMock,
        ) as biomass,
        patch(
            "RUFAS.biophysical.field.soil.carbon_cycling.residue_partition.ResiduePartition.add_residue_to_pools"
        ) as add_residue,
    ):
        field._assess_dormancy(daylength, rainfall)

    if daylength <= threshold_daylength:
        assert dormancy.call_count == 1
        assert biomass.call_count == 1
        assert add_residue.call_count == 1
    else:
        dormancy.assert_not_called()
        biomass.assert_not_called()


@pytest.mark.parametrize(
    "mix_name,requested_n,requested_p,requested_k,ammonium_fraction,depth,remainder,year,day,field_size,"
    "fertilizer_applied",
    {
        ("test_mix_1", 80.0, 30.0, 20.0, 0.0, 0.0, 1.0, 1993, 100, 3.1, True),
        ("test_mix_2", 150.0, 89.0, 20.0, 0.5, 25.0, 0.89, 2001, 240, 1.3, True),
        ("test_mix_3", 10.0, 90.33, 20.0, 1.0, 100.0, 0.5, 1992, 30, 2.44, True),
        ("test_mix_4", 0.0, 50.0, 20.0, 0.0, 0.0, 1.0, 1996, 60, 1.45, True),
        ("test_mix_5", 67.5, 0.0, 20.0, 0.2, 0.0, 1.0, 1998, 200, 2.3, True),
        ("test_mix_6", 0.0, 0.0, 0.0, 0.3, 0.0, 1.0, 1988, 120, 0.5, False),
    },
)
def test_execute_fertilizer_application(
    mocker: MockerFixture,
    mix_name: str,
    requested_n: float,
    requested_p: float,
    requested_k: float,
    ammonium_fraction: float,
    depth: float,
    remainder: float,
    year: int,
    day: int,
    field_size: float,
    fertilizer_applied: bool,
) -> None:
    """Tests that fertilizer applications are being correctly executed and recorded."""
    field_data = FieldData(name="test", field_size=field_size)
    field = Field(
        field_data=field_data,
        fertilizer_mixes={mix_name: {"N": 0.3, "P": 0.2, "K": 0.5, "ammonium_fraction": ammonium_fraction}},
    )
    formulate = mocker.patch.object(
        field,
        "_formulate_fertilizer_required",
        return_value={"total_mass": 100, "nitrogen_mass": 20, "phosphorus_mass": 15, "potassium_mass": 10},
    )
    apply = mocker.patch.object(field.fertilizer_applicator, "apply_fertilizer")
    record = mocker.patch.object(field, "_record_fertilizer_application")

    with patch("RUFAS.output_manager.Utility.get_timestamp") as mocked_timestamp:
        mocked_timestamp.return_value = "00-Jan-1970_Thu_00-00-00"

        field._execute_fertilizer_application(
            mix_name, requested_n, requested_p, requested_k, depth, remainder, year, day
        )

        if fertilizer_applied:
            formulate.assert_called_once_with(0.3, 0.2, 0.5, requested_n, requested_p, requested_k)
            apply.assert_called_once_with(15, 20.0, ammonium_fraction, depth, remainder, field_size)
            record.assert_called_once_with(mix_name, 100, 20, 15, 10, ammonium_fraction, depth, remainder, year, day)
        else:
            expected_info_map = {
                "suffix": "field='test'",
                "year": year,
                "day": day,
                "timestamp": "00-Jan-1970_Thu_00-00-00",
            }
            expected_log_message = "Tried to apply fertilizer with no nitrogen, phosphorus, or potassium requested."
            actual = field.om.logs_pool["Field._execute_fertilizer_application.fertilizer_application_log.field='test'"]
            assert actual["info_maps"].__contains__(expected_info_map)
            assert actual["values"].__contains__(expected_log_message)
            formulate.assert_not_called()
            apply.assert_not_called()
            record.assert_not_called()


@pytest.mark.parametrize(
    "field_name,mix_name,available_mixes",
    [
        ("test_field_1", "halo_alien_mix", {}),
        ("test_field_2", "101_0_0", {"50_22_12": {"N": 0.5, "P": 0.22, "K": 0.12, "ammonium_fraction": 0.0}}),
    ],
)
def test_execute_fertilizer_application_error(
    field_name: str, mix_name: str, available_mixes: dict[str, dict[str, float]]
) -> None:
    """
    Tests that errors are correctly raised when a mix is specified to be used but is not listed in the available mixes.
    """
    field = Field(
        field_data=FieldData(name=field_name),
        fertilizer_mixes=available_mixes,
    )
    with pytest.raises(KeyError):
        field._execute_fertilizer_application(mix_name, 10.0, 10.0, 10.0, 0.0, 1.0, 1994, 120)


@pytest.mark.parametrize(
    "depth,remainder,expected_depth,expected_remainder,invalid_combination",
    [
        (1000.0, 0.1, 950.0, 0.1, False),
        (100.0, 1.0, 0.0, 1.0, True),
        (0.0, 0.9, 0.0, 1.0, True),
    ],
)
def test_execute_fertilizer_application_with_invalid_args(
    depth: float,
    remainder: float,
    expected_depth: float,
    expected_remainder: float,
    invalid_combination: bool,
) -> None:
    """Tests that fertilizer applications with invalid arguments are caught, recorded in the OutputManager and execution
    with corrected values takes place."""
    field = Field(
        field_data=FieldData(name="test", field_size=1.2),
    )
    field.soil.data.soil_layers[-1].bottom_depth = 950.0
    with (
        patch(
            "RUFAS.biophysical.field.field.field.Field._record_nutrient_application_error",
            new_callable=MagicMock,
        ) as patched_error,
        patch(
            "RUFAS.biophysical.field.field.field.Field._formulate_fertilizer_required",
            new_callable=MagicMock,
            return_value={
                "total_mass": 100.0,
                "phosphorus_mass": 50.0,
                "nitrogen_mass": 50.0,
                "potassium_mass": 0.0,
            },
        ) as patched_formulator,
        patch(
            "RUFAS.biophysical.field.field.fertilizer_application.FertilizerApplication.apply_fertilizer",
            new_callable=MagicMock,
        ) as patched_applicator,
        patch(
            "RUFAS.biophysical.field.field.field.Field._record_fertilizer_application",
            new_callable=MagicMock,
        ) as patched_recorder,
    ):
        field._execute_fertilizer_application("26_4_24", 50.0, 50.0, 50.0, depth, remainder, 1994, 200)

        if invalid_combination:
            patched_error.assert_called_once_with(depth, remainder, "fertilizer_application_error", 1994, 200)
        else:
            patched_error.assert_called_once_with(depth, None, "fertilizer_application_error", 1994, 200)
        patched_formulator.assert_called_once_with(0.26, 0.04, 0.24, 50.0, 50.0, 50.0)
        patched_applicator.assert_called_once_with(50.0, 50.0, 0.0, expected_depth, expected_remainder, 1.2)
        patched_recorder.assert_called_once_with(
            "26_4_24",
            100.0,
            50.0,
            50.0,
            0.0,
            0.0,
            expected_depth,
            expected_remainder,
            1994,
            200,
        )


@pytest.mark.parametrize(
    "nitrogen,phosphorus,mixes,expected",
    [
        (
            100,
            20,
            {
                "100_0_0": {"N": 1.0, "P": 0.0, "K": 0.0},
                "26_4_24": {"N": 0.26, "P": 0.04, "K": 0.24},
            },
            "26_4_24",
        ),
        (50, 60, {"30_40_50": {"N": 0.3, "P": 0.4, "K": 0.5}}, "30_40_50"),
        (
            22.5,
            33,
            {
                "25_15_28": {"N": 0.25, "P": 0.15, "K": 0.28},
                "33_40_3": {"N": 0.33, "P": 0.4, "K": 0.28},
                "40_22_6": {"N": 0.4, "P": 0.22, "K": 0.06},
            },
            "33_40_3",
        ),
        (
            245.0,
            43.0,
            {
                "0_0_60": {"N": 0.0, "P": 0.0, "K": 0.6},
                "26_4_24": {"N": 0.26, "P": 0.04, "K": 0.24},
            },
            "26_4_24",
        ),
    ],
)
def test_determine_optimal_fertilizer_mix(
    nitrogen: float,
    phosphorus: float,
    mixes: Dict[str, Dict[str, float]],
    expected: float,
) -> None:
    """Tests that the optimal mix for meeting the requested nutrients is found correctly."""
    actual = Field._determine_optimal_fertilizer_mix(nitrogen, phosphorus, mixes)
    assert actual == expected


@pytest.mark.parametrize(
    "nitrogen_frac,phosphorus_frac,potassium_frac,requested_nitrogen,requested_phosphorus,requested_potassium,expected",
    [
        (
            0.2,
            0.1,
            0.3,
            100.0,
            80.0,
            40.0,
            {
                "total_mass": 800.0,
                "nitrogen_mass": 160.0,
                "phosphorus_mass": 80.0,
                "potassium_mass": 240.0,
            },
        ),
        (
            0.82,
            0.0,
            0.0,
            200.0,
            50.0,
            30.0,
            {
                "total_mass": 243.90243902439025,
                "nitrogen_mass": 200.0,
                "phosphorus_mass": 0.0,
                "potassium_mass": 0.0,
            },
        ),
        (
            0.4,
            0.2,
            0.1,
            80.0,
            40.0,
            20.0,
            {
                "total_mass": 200.0,
                "nitrogen_mass": 80.0,
                "phosphorus_mass": 40.0,
                "potassium_mass": 20.0,
            },
        ),
        (
            0.05,
            0.1,
            0.3,
            45.0,
            100.0,
            60.0,
            {
                "total_mass": 1000.0,
                "nitrogen_mass": 50.0,
                "phosphorus_mass": 100.0,
                "potassium_mass": 300.0,
            },
        ),
        (
            0.2,
            0.2,
            0.2,
            20.0,
            20.0,
            40.0,
            {
                "total_mass": 200.0,
                "nitrogen_mass": 40.0,
                "phosphorus_mass": 40.0,
                "potassium_mass": 40.0,
            },
        ),
        (
            0.0,
            0.0,
            0.5,
            0.0,
            0.0,
            1000.0,
            {
                "total_mass": 2000.0,
                "nitrogen_mass": 0.0,
                "phosphorus_mass": 0.0,
                "potassium_mass": 1000.0,
            },
        ),
    ],
)
def test_formulate_fertilizer_required(
    nitrogen_frac: float,
    phosphorus_frac: float,
    potassium_frac: float,
    requested_nitrogen: float,
    requested_phosphorus: float,
    requested_potassium: float,
    expected: Dict[str, float],
) -> None:
    """Tests that fertilizer formulations are made correctly."""
    actual = Field._formulate_fertilizer_required(
        nitrogen_frac,
        phosphorus_frac,
        potassium_frac,
        requested_nitrogen,
        requested_phosphorus,
        requested_potassium,
    )
    assert actual == expected


@pytest.mark.parametrize(
    "mix_name,total_mass,nitrogen_mass,phosphorus_mass,potassium_mass,ammonium_fraction,depth,remainder,year,day,"
    "field_name,field_size",
    [
        ("mix_1", 100, 20, 20, 20, 0.5, 35.0, 0.8, 1992, 90, "field_1", 1.4),
        ("mix_2", 30, 10, 3, 3, 0.1, 0.0, 1.0, 1994, 120, "field_2", 4.3),
    ],
)
def test_record_fertilizer_application(
    mix_name: str,
    total_mass: float,
    nitrogen_mass: float,
    phosphorus_mass: float,
    potassium_mass: float,
    ammonium_fraction: float,
    depth: float,
    remainder: float,
    year: int,
    day: int,
    field_name: str,
    field_size: float,
) -> None:
    """Tests that fertilizer applications are correctly recorded in the OutputManager."""
    field = Field(
        field_data=FieldData(name=field_name, field_size=field_size),
    )

    with patch(
        "RUFAS.biophysical.field.soil.soil_data.SoilData.average_clay_percent",
        new_callable=PropertyMock,
        return_value=10.0,
    ) as clay:
        field._record_fertilizer_application(
            mix_name,
            total_mass,
            nitrogen_mass,
            phosphorus_mass,
            potassium_mass,
            ammonium_fraction,
            depth,
            remainder,
            year,
            day,
        )

        clay.assert_called_once()

    expected_units = {
        "mass": MeasurementUnits.KILOGRAMS.value,
        "nitrogen": MeasurementUnits.KILOGRAMS.value,
        "phosphorus": MeasurementUnits.KILOGRAMS.value,
        "potassium": MeasurementUnits.KILOGRAMS.value,
        "ammonium_fraction": MeasurementUnits.UNITLESS.value,
        "application_depth": MeasurementUnits.MILLIMETERS.value,
        "surface_remainder_fraction": MeasurementUnits.UNITLESS.value,
        "year": MeasurementUnits.CALENDAR_YEAR.value,
        "day": MeasurementUnits.ORDINAL_DAY.value,
        "field_size": MeasurementUnits.HECTARE.value,
        "field_name": MeasurementUnits.UNITLESS.value,
        "average_clay_percent": MeasurementUnits.PERCENT.value,
    }

    expected_info_map = {"suffix": f"field='{field_name}'", "mix_name": mix_name, "units": expected_units}
    expected_value = {
        "mass": total_mass,
        "nitrogen": nitrogen_mass,
        "phosphorus": phosphorus_mass,
        "potassium": potassium_mass,
        "ammonium_fraction": ammonium_fraction,
        "application_depth": depth,
        "surface_remainder_fraction": remainder,
        "year": year,
        "day": day,
        "field_size": field_size,
        "field_name": field_name,
        "average_clay_percent": 10.0,
    }

    actual = field.om.variables_pool[
        f"Field._record_fertilizer_application.fertilizer_application.field='{field_name}'"
    ]
    assert actual["info_maps"].__contains__(expected_info_map)
    assert actual["values"].__contains__(expected_value)


@pytest.mark.parametrize(
    "nitrogen,phosphorus,coverage,manure_type,depth,remainder,year,day,supplement,"
    "fertilizer_applied,only_nitrogen_unmet,supplied_manure,expected_request,"
    "expected_unmet_nitrogen,expected_unmet_phosphorus",
    [
        (
            75.0,
            75.0,
            0.9,
            ManureType.LIQUID,
            0.0,
            1.0,
            1993,
            175,
            ManureSupplementMethod.SYNTHETIC_FERTILIZER,
            True,
            False,
            NutrientRequestResults(
                nitrogen=50.0,
                phosphorus=50.0,
                dry_matter=250.0,
                dry_matter_fraction=0.33,
                organic_nitrogen_fraction=0.3,
                inorganic_nitrogen_fraction=0.7,
                ammonium_nitrogen_fraction=0.25,
                organic_phosphorus_fraction=0.5,
                inorganic_phosphorus_fraction=0.5,
            ),
            NutrientRequest(
                nitrogen=75.0, phosphorus=75.0, manure_type=ManureType.LIQUID, use_supplemental_manure=False
            ),
            25.0,
            25.0,
        ),
        (
            100.0,
            0.0,
            0.88,
            ManureType.LIQUID,
            120.0,
            0.7,
            2003,
            200,
            True,
            True,
            True,
            NutrientRequestResults(
                nitrogen=50.0,
                phosphorus=50.0,
                dry_matter=250.0,
                dry_matter_fraction=0.33,
                organic_nitrogen_fraction=0.3,
                inorganic_nitrogen_fraction=0.7,
                ammonium_nitrogen_fraction=0.25,
                organic_phosphorus_fraction=0.4,
                inorganic_phosphorus_fraction=0.6,
            ),
            NutrientRequest(
                nitrogen=100.0, phosphorus=0.0, manure_type=ManureType.LIQUID, use_supplemental_manure=False
            ),
            50.0,
            0.0,
        ),
        (
            50.0,
            50.0,
            0.91,
            ManureType.LIQUID,
            200.0,
            0.45,
            1998,
            155,
            True,
            False,
            False,
            NutrientRequestResults(
                nitrogen=50.0,
                phosphorus=50.0,
                dry_matter=250.0,
                dry_matter_fraction=0.33,
                organic_nitrogen_fraction=0.3,
                inorganic_nitrogen_fraction=0.7,
                ammonium_nitrogen_fraction=0.25,
                organic_phosphorus_fraction=0.544,
                inorganic_phosphorus_fraction=0.456,
            ),
            NutrientRequest(
                nitrogen=50.0, phosphorus=50.0, manure_type=ManureType.LIQUID, use_supplemental_manure=False
            ),
            0.0,
            0.0,
        ),
        (
            65.0,
            40.0,
            0.77,
            ManureType.LIQUID,
            75.0,
            0.78,
            1999,
            160,
            True,
            True,
            False,
            None,
            NutrientRequest(
                nitrogen=65.0, phosphorus=40.0, manure_type=ManureType.LIQUID, use_supplemental_manure=False
            ),
            65.0,
            40.0,
        ),
        (
            0,
            0,
            0.5,
            0.0,
            ManureType.LIQUID,
            1.0,
            1996,
            155,
            True,
            False,
            False,
            None,
            None,
            0.0,
            0.0,
        ),
        (
            75.0,
            50.0,
            0.7,
            ManureType.LIQUID,
            0.0,
            1.0,
            2010,
            120,
            ManureSupplementMethod.NONE,
            True,
            True,
            NutrientRequestResults(
                nitrogen=50.0,
                phosphorus=50.0,
                dry_matter=250.0,
                dry_matter_fraction=0.33,
                organic_nitrogen_fraction=0.3,
                inorganic_nitrogen_fraction=0.7,
                ammonium_nitrogen_fraction=0.25,
                organic_phosphorus_fraction=0.544,
                inorganic_phosphorus_fraction=0.456,
            ),
            NutrientRequest(
                nitrogen=75.0, phosphorus=50.0, manure_type=ManureType.LIQUID, use_supplemental_manure=False
            ),
            25.0,
            0.0,
        ),
        (
            50.0,
            50.0,
            0.7,
            ManureType.LIQUID,
            0.0,
            1.0,
            2010,
            120,
            ManureSupplementMethod.NONE,
            False,
            False,
            NutrientRequestResults(
                nitrogen=50.0,
                phosphorus=50.0,
                dry_matter=250.0,
                dry_matter_fraction=0.33,
                organic_nitrogen_fraction=0.3,
                inorganic_nitrogen_fraction=0.7,
                ammonium_nitrogen_fraction=0.25,
                organic_phosphorus_fraction=0.544,
                inorganic_phosphorus_fraction=0.456,
            ),
            NutrientRequest(
                nitrogen=50.0, phosphorus=50.0, manure_type=ManureType.LIQUID, use_supplemental_manure=False
            ),
            50.0,
            0.0,
        ),
    ],
)
def test_execute_manure_application(
    mocker: MockerFixture,
    nitrogen: float,
    phosphorus: float,
    manure_type: ManureType,
    coverage: float,
    depth: float,
    remainder: float,
    year: int,
    day: int,
    supplement: ManureSupplementMethod,
    fertilizer_applied: bool,
    only_nitrogen_unmet: bool,
    supplied_manure: NutrientRequestResults,
    expected_request: NutrientRequest,
    expected_unmet_nitrogen: float,
    expected_unmet_phosphorus: float,
) -> None:
    """Tests that manure is applied to the soil correctly."""
    field = Field(field_data=FieldData(name="test", field_size=1.4))
    mock_add_manure_water = mocker.patch.object(
        field,
        "_add_manure_water",
        return_value=None,
    )
    field.manure_applicator.apply_machine_manure = MagicMock()
    field._record_manure_application = MagicMock()
    field._determine_optimal_fertilizer_mix = MagicMock(return_value="expected_optimal_mix")
    field._execute_fertilizer_application = MagicMock()

    warn = mocker.patch.object(field.om, "add_warning")

    field._execute_manure_application(
        nitrogen,
        phosphorus,
        manure_type,
        coverage,
        depth,
        remainder,
        year,
        day,
        supplied_manure,
        ManureSupplementMethod.NONE,
    )

    expected_total_inorganic_fraction = 0.14
    expected_total_organic_fraction = 0.06

    if supplied_manure is not None:
        mock_add_manure_water.assert_called_once_with(supplied_manure, manure_type)
        field.manure_applicator.apply_machine_manure.assert_called_once_with(
            dry_matter_mass=supplied_manure.dry_matter,
            dry_matter_fraction=supplied_manure.dry_matter_fraction,
            total_phosphorus_mass=supplied_manure.phosphorus,
            field_coverage=coverage,
            application_depth=depth,
            surface_remainder_fraction=remainder,
            field_size=1.4,
            inorganic_nitrogen_fraction=pytest.approx(expected_total_inorganic_fraction),
            ammonium_fraction=supplied_manure.ammonium_nitrogen_fraction,
            organic_nitrogen_fraction=pytest.approx(expected_total_organic_fraction),
            water_extractable_inorganic_phosphorus_fraction=supplied_manure.inorganic_phosphorus_fraction,
        )
        expected_record_manure_application_calls = [
            mocker.call(
                dry_matter_mass=supplied_manure.dry_matter,
                dry_matter_fraction=supplied_manure.dry_matter_fraction,
                field_coverage=coverage,
                nitrogen=supplied_manure.nitrogen,
                phosphorus=supplied_manure.phosphorus,
                potassium=None,
                application_depth=depth,
                surface_remainder_fraction=remainder,
                year=year,
                day=day,
                output_name="manure_application",
            ),
            mocker.call(
                dry_matter_mass=0.0,
                dry_matter_fraction=0.0,
                field_coverage=coverage,
                nitrogen=expected_request.nitrogen,
                phosphorus=expected_request.phosphorus,
                potassium=None,
                application_depth=depth,
                surface_remainder_fraction=remainder,
                year=year,
                day=day,
                output_name="manure_request",
            ),
        ]
        field._record_manure_application.assert_has_calls(expected_record_manure_application_calls)

        if fertilizer_applied and not supplement == ManureSupplementMethod.NONE:
            warn.assert_called_once()
            field._determine_optimal_fertilizer_mix.assert_not_called()
            field._execute_fertilizer_application.assert_not_called()
        elif not fertilizer_applied and not supplement == ManureSupplementMethod.NONE:
            warn.assert_not_called()
            field._determine_optimal_fertilizer_mix.assert_not_called()
            field._execute_fertilizer_application.assert_not_called()
        elif fertilizer_applied and only_nitrogen_unmet and supplement == ManureSupplementMethod.SYNTHETIC_FERTILIZER:
            warn.assert_not_called()
            field._determine_optimal_fertilizer_mix.assert_not_called()
            field._execute_fertilizer_application.assert_called_once_with(
                "100_0_0",
                expected_unmet_nitrogen,
                expected_unmet_phosphorus,
                0,
                depth,
                remainder,
                year,
                day,
            )
        elif fertilizer_applied and not only_nitrogen_unmet and ManureSupplementMethod.SYNTHETIC_FERTILIZER:
            warn.assert_not_called()
            field._determine_optimal_fertilizer_mix.assert_called_once_with(
                expected_unmet_nitrogen,
                expected_unmet_phosphorus,
                field.available_fertilizer_mixes,
            )
            field._execute_fertilizer_application.assert_called_once_with(
                "expected_optimal_mix",
                expected_unmet_nitrogen,
                expected_unmet_phosphorus,
                0,
                depth,
                remainder,
                year,
                day,
            )


def test_apply_and_record_manure_application(mocker: MockerFixture) -> None:
    """Tests that the manure application is applied and recorded correctly."""
    field = Field(field_data=MagicMock(name="test", field_size=1.2))

    manure_supplied = NutrientRequestResults(
        nitrogen=60.0,
        phosphorus=30.0,
        dry_matter=200.0,
        dry_matter_fraction=0.35,
        organic_nitrogen_fraction=0.3,
        inorganic_nitrogen_fraction=0.7,
        ammonium_nitrogen_fraction=0.25,
        organic_phosphorus_fraction=0.4,
        inorganic_phosphorus_fraction=0.6,
    )

    manure_type = ManureType.LIQUID
    coverage = 0.85
    original_depth = 150.0
    original_remainder = 0.5
    year = 2025
    day = 100

    validated_depth = 120.0
    validated_remainder = 0.65

    mock_add_manure_water = mocker.patch.object(
        field,
        "_add_manure_water",
        return_value=None,
    )
    mock_validate_application_depth_and_fraction = mocker.patch.object(
        field,
        "_validate_application_depth_and_fraction",
        return_value=(validated_depth, validated_remainder),
    )
    mock_manure_applicator = mocker.patch.object(
        field.manure_applicator,
        "apply_machine_manure",
        return_value=None,
    )
    mock_record_manure_application = mocker.patch.object(field, "_record_manure_application", return_value=None)

    result = field._apply_and_record_manure_application(
        manure_supplied, manure_type, coverage, original_depth, original_remainder, year, day
    )

    assert result == {
        "supplied_nitrogen": 60.0,
        "supplied_phosphorus": 30.0,
        "application_depth": validated_depth,
        "surface_remainder_fraction": validated_remainder,
    }

    mock_add_manure_water.assert_called_once_with(manure_supplied, manure_type)

    mock_validate_application_depth_and_fraction.assert_called_once_with(original_depth, original_remainder, year, day)

    mock_manure_applicator.assert_called_once_with(
        dry_matter_mass=manure_supplied.dry_matter,
        dry_matter_fraction=manure_supplied.dry_matter_fraction,
        total_phosphorus_mass=manure_supplied.phosphorus,
        field_coverage=coverage,
        application_depth=validated_depth,
        surface_remainder_fraction=validated_remainder,
        field_size=1.2,
        inorganic_nitrogen_fraction=pytest.approx((60.0 / 200.0) * 0.7),
        ammonium_fraction=manure_supplied.ammonium_nitrogen_fraction,
        organic_nitrogen_fraction=pytest.approx((60.0 / 200.0) * 0.3),
        water_extractable_inorganic_phosphorus_fraction=manure_supplied.inorganic_phosphorus_fraction,
    )

    mock_record_manure_application.assert_called_once_with(
        dry_matter_mass=manure_supplied.dry_matter,
        dry_matter_fraction=manure_supplied.dry_matter_fraction,
        field_coverage=coverage,
        nitrogen=60.0,
        phosphorus=30.0,
        potassium=None,
        application_depth=validated_depth,
        surface_remainder_fraction=validated_remainder,
        year=year,
        day=day,
        output_name="manure_application",
    )


@pytest.mark.parametrize(
    "depth, remainder, soil_max_depth, expected_depth, expected_remainder, expect_log",
    [
        (0.0, 0.5, 150.0, 0.0, 1.0, True),
        (50.0, 1.0, 150.0, 0.0, 1.0, True),
        (200.0, 0.5, 150.0, 150.0, 0.5, True),
        (75.0, 0.5, 150.0, 75.0, 0.5, False),
    ],
)
def test_validate_application_depth_and_fraction(
    mocker: MockerFixture,
    depth: float,
    remainder: float,
    soil_max_depth: float,
    expected_depth: float,
    expected_remainder: float,
    expect_log: bool,
) -> None:
    """Tests that the application depth and fraction are validated correctly."""
    field = Field(field_data=MagicMock(name="test", field_size=1.2))
    field.soil = MagicMock()
    field.soil.data.soil_layers = [MagicMock(bottom_depth=soil_max_depth)]
    # field._record_nutrient_application_error = mocker.MagicMock()
    mock_record_nutrient_application_error = mocker.patch.object(
        field,
        "_record_nutrient_application_error",
        return_value=None,
    )

    result = field._validate_application_depth_and_fraction(depth, remainder, 2025, 101)

    assert result == (expected_depth, expected_remainder)

    if expect_log:
        mock_record_nutrient_application_error.assert_called()
    else:
        mock_record_nutrient_application_error.assert_not_called()


def test_validate_application_depth_and_fraction_raises_for_missing_soil_layers() -> None:
    field = Field(field_data=MagicMock(name="test", field_size=1.2))
    field.soil = MagicMock()
    field.soil.data.soil_layers = None

    with pytest.raises(ValueError, match="soil_layers is not initialized"):
        field._validate_application_depth_and_fraction(50.0, 0.5, 2025, 101)


def test_validate_application_depth_and_fraction_raises_for_missing_bottom_depth() -> None:
    field = Field(field_data=MagicMock(name="test", field_size=1.2))
    field.soil = MagicMock()
    mock_layer = MagicMock()
    mock_layer.bottom_depth = None
    field.soil.data.soil_layers = [mock_layer]

    with pytest.raises(ValueError, match="bottom_depth is not set for the last soil layer"):
        field._validate_application_depth_and_fraction(50.0, 0.5, 2025, 101)


@pytest.mark.parametrize(
    "requested_n, requested_p, supplied_n, supplied_p, method, unmet_n, unmet_p, expect_log, expect_warn,"
    "expect_fertilizer, only_nitrogen_unmet",
    [
        (50.0, 50.0, 50.0, 50.0, ManureSupplementMethod.SYNTHETIC_FERTILIZER, 0.0, 0.0, True, False, False, False),
        (60.0, 40.0, 50.0, 40.0, ManureSupplementMethod.NONE, 10.0, 0.0, False, True, False, False),
        (60.0, 40.0, 50.0, 40.0, ManureSupplementMethod.SYNTHETIC_FERTILIZER, 10.0, 0.0, True, False, True, True),
        (
            80.0,
            80.0,
            50.0,
            50.0,
            ManureSupplementMethod.SYNTHETIC_FERTILIZER_AND_MANURE,
            30.0,
            30.0,
            True,
            False,
            True,
            False,
        ),
        (70.0, 70.0, 50.0, 50.0, "UNSUPPORTED_METHOD", 20.0, 20.0, False, True, False, False),
    ],
)
def test_handle_unmet_nutrients(
    mocker: MockerFixture,
    requested_n: float,
    requested_p: float,
    supplied_n: float,
    supplied_p: float,
    method: ManureSupplementMethod,
    unmet_n: float,
    unmet_p: float,
    expect_log: bool,
    expect_warn: bool,
    expect_fertilizer: bool,
    only_nitrogen_unmet: bool,
) -> None:
    """Tests that the handling of unmet nutrients is performed correctly."""
    field = Field(field_data=MagicMock(name="test", field_size=1.2))
    field.om = MagicMock()
    field.ONLY_NITROGEN_MIX = "100_0_0"
    field.available_fertilizer_mixes = {
        "mix1": {"N": 0.0, "P": 0.0},
        "mix2": {"N": 0.0, "P": 0.0},
    }
    mock_determine_optimal_fertilizer_mix = mocker.patch.object(
        field,
        "_determine_optimal_fertilizer_mix",
        return_value="optimal_mix",
    )
    mock_execute_fertilizer_application = mocker.patch.object(
        field,
        "_execute_fertilizer_application",
        return_value=None,
    )

    application_depth = 100.0
    surface_remainder = 0.5

    field._handle_unmet_nutrients(
        requested_n,
        requested_p,
        supplied_n,
        supplied_p,
        application_depth,
        surface_remainder,
        method,
        2025,
        150,
    )

    if expect_log:
        field.om.add_log.assert_called()
    else:
        field.om.add_log.assert_not_called()

    if expect_warn:
        field.om.add_warning.assert_called()
    else:
        field.om.add_warning.assert_not_called()

    if expect_fertilizer:
        if only_nitrogen_unmet:
            mock_determine_optimal_fertilizer_mix.assert_not_called()
            mock_execute_fertilizer_application.assert_called_once_with(
                "100_0_0",
                unmet_n,
                unmet_p,
                0,
                application_depth,
                surface_remainder,
                2025,
                150,
            )
        else:
            mock_determine_optimal_fertilizer_mix.assert_called_once_with(
                unmet_n, unmet_p, field.available_fertilizer_mixes
            )
            mock_execute_fertilizer_application.assert_called_once_with(
                "optimal_mix",
                unmet_n,
                unmet_p,
                0,
                application_depth,
                surface_remainder,
                2025,
                150,
            )
    else:
        mock_execute_fertilizer_application.assert_not_called()


@pytest.mark.parametrize(
    "depth,remainder,expected_depth,expected_remainder,invalid_combination",
    [
        (100.0, 1.0, 0.0, 1.0, True),
        (0.0, 0.76, 0.0, 1.0, True),
        (1000.0, 0.2, 950.0, 0.2, False),
    ],
)
def test_execute_manure_application_with_invalid_args(
    mocker: MockerFixture,
    depth: float,
    remainder: float,
    expected_depth: float,
    expected_remainder: float,
    invalid_combination: bool,
) -> None:
    """Tests that the manure application executor raises errors and runs correctly when invalid arguments are passed."""
    supplied_nutrients = NutrientRequestResults(
        nitrogen=50.0,
        phosphorus=50.0,
        total_manure_mass=150.0,
        dry_matter=100.0,
        dry_matter_fraction=0.66,
    )
    field = Field(field_data=FieldData(name="test", field_size=1.89))
    field.soil.data.soil_layers[-1].bottom_depth = 950.0
    expected_total_inorganic_fraction = 0.15
    expected_total_organic_fraction = 0.35
    mock_add_manure_water = mocker.patch.object(
        field,
        "_add_manure_water",
        new_callable=MagicMock,
        return_value=None,
    )

    with (
        patch(
            "RUFAS.biophysical.field.field.field.Field._record_nutrient_application_error",
            new_callable=MagicMock,
        ) as patched_error,
        patch(
            "RUFAS.biophysical.field.field.manure_application.ManureApplication.apply_machine_manure",
            new_callable=MagicMock,
        ) as patched_manure_applicator,
        patch(
            "RUFAS.biophysical.field.field.field.Field._record_manure_application",
            new_callable=MagicMock,
        ) as patched_recorder,
        patch(
            "RUFAS.biophysical.field.field.field.Field._determine_optimal_fertilizer_mix",
            new_callable=MagicMock,
            return_value="26_4_24",
        ) as patched_optimizer,
        patch(
            "RUFAS.biophysical.field.field.field.Field._execute_fertilizer_application",
            new_callable=MagicMock,
        ) as patched_fertilizer_applicator,
    ):
        field._execute_manure_application(
            50.0,
            50.0,
            ManureType.LIQUID,
            0.8,
            depth,
            remainder,
            2000,
            133,
            supplied_nutrients,
            ManureSupplementMethod.NONE,
        )

        mock_add_manure_water.assert_called_once_with(supplied_nutrients, ManureType.LIQUID)
        if invalid_combination:
            patched_error.assert_called_once_with(depth, remainder, "manure_application_error", 2000, 133)
        else:
            patched_error.assert_called_once_with(depth, None, "manure_application_error", 2000, 133)
        patched_manure_applicator.assert_called_once_with(
            dry_matter_mass=100.0,
            dry_matter_fraction=0.66,
            total_phosphorus_mass=50.0,
            field_coverage=0.8,
            application_depth=expected_depth,
            surface_remainder_fraction=expected_remainder,
            field_size=1.89,
            inorganic_nitrogen_fraction=expected_total_inorganic_fraction,
            ammonium_fraction=supplied_nutrients.ammonium_nitrogen_fraction,
            organic_nitrogen_fraction=expected_total_organic_fraction,
            water_extractable_inorganic_phosphorus_fraction=0.5,
        )
        expected_record_manure_application_calls = [
            mocker.call(
                dry_matter_mass=100.0,
                dry_matter_fraction=0.66,
                field_coverage=0.8,
                nitrogen=50.0,
                output_name="manure_application",
                phosphorus=50.0,
                potassium=None,
                application_depth=expected_depth,
                surface_remainder_fraction=expected_remainder,
                year=2000,
                day=133,
            ),
            mocker.call(
                dry_matter_mass=0.0,
                dry_matter_fraction=0.0,
                field_coverage=0.8,
                nitrogen=50.0,
                phosphorus=50.0,
                potassium=None,
                application_depth=expected_depth,
                surface_remainder_fraction=expected_remainder,
                year=2000,
                day=133,
                output_name="manure_request",
            ),
        ]
        patched_recorder.assert_has_calls(expected_record_manure_application_calls)
        patched_optimizer.assert_not_called()
        patched_fertilizer_applicator.assert_not_called()


@pytest.mark.parametrize(
    "field_name,field_size,dry_mass,dry_fraction,coverage,nitrogen,phosphorus,depth,remainder,"
    "year,day,expected_info,expected_values,potassium",
    [
        (
            "test_1",
            1.3,
            100,
            0.1,
            0.8,
            10,
            15,
            0.0,
            1.0,
            1991,
            75,
            {
                "suffix": "field='test_1'",
                "units": {
                    "dry_matter_mass": MeasurementUnits.DRY_KILOGRAMS.value,
                    "dry_matter_fraction": MeasurementUnits.FRACTION.value,
                    "field_coverage": MeasurementUnits.UNITLESS.value,
                    "application_depth": MeasurementUnits.MILLIMETERS.value,
                    "surface_remainder_fraction": MeasurementUnits.UNITLESS.value,
                    "nitrogen": MeasurementUnits.KILOGRAMS.value,
                    "phosphorus": MeasurementUnits.KILOGRAMS.value,
                    "potassium": MeasurementUnits.KILOGRAMS.value,
                    "day": MeasurementUnits.ORDINAL_DAY.value,
                    "year": MeasurementUnits.CALENDAR_YEAR.value,
                    "field_size": MeasurementUnits.HECTARE.value,
                    "field_name": MeasurementUnits.UNITLESS.value,
                    "average_clay_percent": MeasurementUnits.PERCENT.value,
                },
            },
            {
                "dry_matter_mass": 100,
                "dry_matter_fraction": 0.1,
                "application_depth": 0.0,
                "surface_remainder_fraction": 1.0,
                "field_coverage": 0.8,
                "nitrogen": 10,
                "phosphorus": 15,
                "potassium": 12.5,
                "year": 1991,
                "day": 75,
                "field_size": 1.3,
                "field_name": "test_1",
                "average_clay_percent": 10.0,
            },
            12.5,
        ),
        (
            "test_2",
            2.4,
            144.6,
            0.3,
            0.92,
            40,
            43.1,
            45.0,
            0.85,
            1994,
            200,
            {
                "suffix": "field='test_2'",
                "units": {
                    "dry_matter_mass": MeasurementUnits.DRY_KILOGRAMS.value,
                    "dry_matter_fraction": MeasurementUnits.FRACTION.value,
                    "field_coverage": MeasurementUnits.UNITLESS.value,
                    "application_depth": MeasurementUnits.MILLIMETERS.value,
                    "surface_remainder_fraction": MeasurementUnits.UNITLESS.value,
                    "nitrogen": MeasurementUnits.KILOGRAMS.value,
                    "phosphorus": MeasurementUnits.KILOGRAMS.value,
                    "potassium": MeasurementUnits.KILOGRAMS.value,
                    "day": MeasurementUnits.ORDINAL_DAY.value,
                    "year": MeasurementUnits.CALENDAR_YEAR.value,
                    "field_size": MeasurementUnits.HECTARE.value,
                    "field_name": MeasurementUnits.UNITLESS.value,
                    "average_clay_percent": MeasurementUnits.PERCENT.value,
                },
            },
            {
                "dry_matter_mass": 144.6,
                "dry_matter_fraction": 0.3,
                "application_depth": 45.0,
                "surface_remainder_fraction": 0.85,
                "field_coverage": 0.92,
                "nitrogen": 40,
                "phosphorus": 43.1,
                "potassium": 14.55,
                "year": 1994,
                "day": 200,
                "field_size": 2.4,
                "field_name": "test_2",
                "average_clay_percent": 10.0,
            },
            14.55,
        ),
        (
            "test_3",
            0.66,
            266.5,
            0.44,
            0.95,
            100.5,
            78.0,
            120.0,
            0.7,
            2009,
            150,
            {
                "suffix": "field='test_3'",
                "units": {
                    "dry_matter_mass": MeasurementUnits.DRY_KILOGRAMS.value,
                    "dry_matter_fraction": MeasurementUnits.FRACTION.value,
                    "field_coverage": MeasurementUnits.UNITLESS.value,
                    "application_depth": MeasurementUnits.MILLIMETERS.value,
                    "surface_remainder_fraction": MeasurementUnits.UNITLESS.value,
                    "nitrogen": MeasurementUnits.KILOGRAMS.value,
                    "phosphorus": MeasurementUnits.KILOGRAMS.value,
                    "potassium": MeasurementUnits.KILOGRAMS.value,
                    "day": MeasurementUnits.ORDINAL_DAY.value,
                    "year": MeasurementUnits.CALENDAR_YEAR.value,
                    "field_size": MeasurementUnits.HECTARE.value,
                    "field_name": MeasurementUnits.UNITLESS.value,
                    "average_clay_percent": MeasurementUnits.PERCENT.value,
                },
            },
            {
                "dry_matter_mass": 266.5,
                "dry_matter_fraction": 0.44,
                "application_depth": 120.0,
                "surface_remainder_fraction": 0.7,
                "field_coverage": 0.95,
                "year": 2009,
                "day": 150,
                "nitrogen": 100.5,
                "phosphorus": 78.0,
                "potassium": None,
                "field_size": 0.66,
                "field_name": "test_3",
                "average_clay_percent": 10.0,
            },
            None,
        ),
    ],
)
def test_record_manure_application(
    field_name: str,
    field_size: float,
    dry_mass: float,
    dry_fraction: float,
    coverage: float,
    nitrogen: float,
    phosphorus: float,
    depth: float,
    remainder: float,
    year: int,
    day: int,
    expected_info: dict[str, Any],
    expected_values: dict[str, Any],
    potassium: float,
) -> None:
    """Tests that manure applications are recorded correctly."""
    field = Field(
        field_data=FieldData(name=field_name, field_size=field_size),
    )

    with patch(
        "RUFAS.biophysical.field.soil.soil_data.SoilData.average_clay_percent",
        new_callable=PropertyMock,
        return_value=10.0,
    ) as clay:
        field._record_manure_application(
            dry_matter_mass=dry_mass,
            dry_matter_fraction=dry_fraction,
            field_coverage=coverage,
            nitrogen=nitrogen,
            phosphorus=phosphorus,
            application_depth=depth,
            surface_remainder_fraction=remainder,
            year=year,
            day=day,
            potassium=potassium,
            output_name="manure_application",
        )

        clay.assert_called_once()

    actual = field.om.variables_pool[
        f"{Field.__name__}.{Field._record_manure_application.__name__}.manure_application.field='{field_name}'"
    ]
    assert actual["info_maps"].__contains__(expected_info)
    assert actual["values"].__contains__(expected_values)


@pytest.mark.parametrize(
    "manure_application,manure_type,expected_liters,converted",
    [
        (NutrientRequestResults(total_manure_mass=100, dry_matter_fraction=0.05), ManureType.LIQUID, 95.0, True),
        (NutrientRequestResults(total_manure_mass=100, dry_matter_fraction=0.05), ManureType.SOLID, 95.0, False),
    ],
)
def test_add_manure_water(
    mocker: MockerFixture,
    manure_application: NutrientRequestResults,
    manure_type: ManureType,
    expected_liters: float,
    converted: bool,
) -> None:
    """Tests that manure water is correctly calculated and stored."""
    field_data = FieldData(field_size=2.3)
    field = Field(field_data=field_data)
    mocked_converter = mocker.patch.object(field.field_data, "convert_liters_to_millimeters", return_value=10.0)

    field._add_manure_water(manure_application, manure_type)

    if converted:
        mocked_converter.assert_called_once_with(expected_liters, 2.3)
        assert field.field_data.manure_water == 10.0
    else:
        mocked_converter.assert_not_called()
        assert field.field_data.manure_water == 0.0


@pytest.mark.parametrize(
    "depth,remainder,name,year,day,expected_info_map,expected_error_message",
    [
        (
            100.0,
            1.0,
            "manure_application_error",
            1998,
            200,
            {
                "suffix": "field='test'",
                "year": 1998,
                "day": 200,
                "timestamp": "00-Jan-1970_Thu_00-00-00",
            },
            "Invalid application depth (100.0) and surface remainder fraction (1.0). Defaulting"
            " to application depth of 0.0 mm and a surface remainder fraction of 1.0.",
        ),
        (
            800.0,
            None,
            "fertilizer_application_error",
            2005,
            100,
            {
                "suffix": "field='test'",
                "year": 2005,
                "day": 100,
                "timestamp": "00-Jan-1970_Thu_00-00-00",
            },
            "Invalid application depth (800.0) is lower than the bottom depth of the soil profile, setting"
            " the application depth to be at the bottom of the soil profile.",
        ),
    ],
)
def test_record_nutrient_application_error(
    depth: float,
    remainder: float,
    name: str,
    year: int,
    day: int,
    expected_info_map: dict[str, Any],
    expected_error_message: str,
) -> None:
    """Tests that manure and fertilizer application errors are correctly recorded to the OutputManager."""
    with patch("RUFAS.output_manager.Utility.get_timestamp") as mocked_timestamp:
        field = Field(field_data=FieldData(name="test"))
        mocked_timestamp.return_value = "00-Jan-1970_Thu_00-00-00"

        field._record_nutrient_application_error(depth, remainder, name, year, day)

        expected_error_name = f"Field._record_nutrient_application_error.{name}.{expected_info_map['suffix']}"
        actual = field.om.errors_pool[expected_error_name]
        assert actual["info_maps"].__contains__(expected_info_map)
        assert actual["values"].__contains__(expected_error_message)


@pytest.mark.parametrize(
    "field_size,crops_growing,residue,light,mean_temp,min_temp,max_temp,annual_mean_temp,transpiration,stressors",
    [
        (1.5, False, 34.5, 128, 22.5, 18.9, 25.6, 19.22, 5.2, True),
        (2.4, True, 40.9, 150, 28, 24.55, 31.2, 17.9, 3.44, False),
        (0.8, True, 12.22, 222, 18.7, 13.44, 23.44, 16.4, 1.33, True),
    ],
)
def test_execute_daily_processes(
    mock_crop_data: CropData,
    field_size: float,
    crops_growing: bool,
    residue: float,
    light: float,
    mean_temp: float,
    min_temp: float,
    max_temp: float,
    annual_mean_temp: float,
    transpiration: float,
    stressors: bool,
) -> None:
    """Tests that all component processes and subroutines are correctly called in Field."""
    with patch.multiple(
        "RUFAS.biophysical.field.crop.crop_data.CropData",
        is_mature=PropertyMock(return_value=not crops_growing),
        is_dormant=PropertyMock(return_value=not crops_growing),
    ):
        field_data = FieldData(
            field_size=field_size,
            current_residue=residue,
            simulate_water_stress=stressors,
            simulate_temp_stress=stressors,
            simulate_nitrogen_stress=stressors,
            simulate_phosphorus_stress=stressors,
        )

        incorp = Field(field_data=field_data)
        crop_1 = Crop(crop_data=mock_crop_data)
        crop_1._data.max_transpiration = transpiration
        crop_2 = Crop(crop_data=mock_crop_data)
        crop_2._data.max_transpiration = transpiration
        incorp.crops = [crop_1, crop_2]
        current_conditions = CurrentDayConditions(
            incoming_light=light,
            mean_air_temperature=mean_temp,
            min_air_temperature=min_temp,
            max_air_temperature=max_temp,
            annual_mean_air_temperature=annual_mean_temp,
        )

        incorp.soil.snow.update_snow = MagicMock()
        incorp._determine_total_above_ground_biomass = MagicMock(return_value=89)
        incorp.soil.soil_temp.daily_soil_temperature_update = MagicMock()
        incorp._cycle_water = MagicMock()
        for crop in incorp.crops:
            crop._heat_units.absorb_heat_units = MagicMock()
            crop._root_development = MagicMock()
            crop._nitrogen_uptake.uptake = MagicMock()
            crop._phosphorus_uptake.uptake = MagicMock()
            crop._growth_constraints.constrain_growth = MagicMock()
            crop._leaf_area_index.grow_canopy = MagicMock()
            crop._biomass_allocation.allocate_biomass = MagicMock()
        mocked_time = MagicMock(RufasTime)
        setattr(mocked_time, "current_calendar_year", 2023)
        setattr(mocked_time, "current_julian_day", 178)

        incorp._execute_daily_processes(current_conditions, mocked_time)

        incorp.soil.snow.update_snow.assert_called_once_with(
            current_day_conditions=current_conditions, day=mocked_time.current_julian_day
        )
        incorp._determine_total_above_ground_biomass.assert_called_once()
        incorp.soil.soil_temp.daily_soil_temperature_update.assert_called_once_with(
            light, mean_temp, min_temp, max_temp, 89 + residue, 0, annual_mean_temp
        )
        incorp._cycle_water.assert_called_once_with(current_conditions, mocked_time)
        for crop in incorp.crops:
            if crops_growing:
                crop._heat_units.absorb_heat_units.assert_called_once_with(mean_temp, min_temp, max_temp)
                crop._root_development.develop_roots.assert_called_once()
                crop._nitrogen_uptake.uptake.assert_called_once_with(incorp.soil.data)
                crop._phosphorus_uptake.uptake.assert_called_once_with(incorp.soil.data)
                crop._growth_constraints.constrain_growth.assert_called_once_with(
                    transpiration,
                    mean_temp,
                    *[stressors] * 4,
                )
                crop._leaf_area_index.grow_canopy.assert_called_once()
                crop._biomass_allocation.allocate_biomass.assert_called_once_with(light)
            else:
                crop._heat_units.absorb_heat_units.assert_not_called()
                crop._root_development.develop_roots.assert_not_called()
                crop._nitrogen_uptake.uptake.assert_not_called()
                crop._phosphorus_uptake.uptake.assert_not_called()
                crop._growth_constraints.constrain_growth.assert_not_called()
                crop._leaf_area_index.grow_canopy.assert_not_called()
                crop._biomass_allocation.allocate_biomass.assert_not_called()


@pytest.mark.parametrize(
    "field_size,rainfall,manure_water,snow_content,runoff,high_water_table,residue,light,min_temp,max_temp,mean_temp,"
    "surface_residue,crop_1_proportion,crop_2_proportion,crops_growing",
    [
        (1.9, 4.66, 3.2, 0.0, 1.22, False, 30.6, 200, 16.5, 20.5, 18.5, 44.5, 0.6, 0.4, True),
        (2.3, 5.6, 1.1, 3.3, 2.1, True, 44.5, 250, 22.33, 25.36, 24.6, 80.4, 0.77, 0.23, False),
        (2.3, 5.6, 0.0, 8.5, 2.1, True, 44.5, 250, 22.33, 25.36, 24.6, 80.4, 0.0, 0.0, False),
    ],
)
def test_cycle_water(
    field_size: float,
    rainfall: float,
    manure_water: float,
    snow_content: float,
    runoff: float,
    high_water_table: bool,
    residue: float,
    light: float,
    min_temp: float,
    max_temp: float,
    mean_temp: float,
    surface_residue: float,
    crop_1_proportion: float,
    crop_2_proportion: float,
    crops_growing: bool,
) -> None:
    """Tests that cycle_water() correctly executes all water processes on its soil profile and the crops it contains."""
    with patch(
        "RUFAS.biophysical.field.crop.crop_data.CropData.in_growing_season",
        new_callable=PropertyMock,
        return_value=crops_growing,
    ):
        soil_data = SoilData(
            field_size=field_size,
            accumulated_runoff=runoff,
            water_evaporated=3.5,
            water_sublimated=1.0,
            snow_content=snow_content,
        )
        soil_data.soil_layers[0].plant_residue = surface_residue
        soil = Soil(soil_data)
        crop_data_1 = CropData(
            field_proportion=crop_1_proportion,
            max_transpiration=44.1,
            cumulative_evaporation=105.5,
            cumulative_transpiration=205.1,
            cumulative_potential_evapotranspiration=400.19,
            water_uptake=3.5,
            **SAMPLE_CROP_CONFIGURATION,
        )
        crop_1 = Crop(crop_data_1)
        crop_data_2 = CropData(
            field_proportion=crop_2_proportion,
            max_transpiration=39.5,
            cumulative_evaporation=112.4,
            cumulative_transpiration=219.2,
            cumulative_potential_evapotranspiration=480.1,
            water_uptake=3.25,
            **SAMPLE_CROP_CONFIGURATION,
        )
        crop_2 = Crop(crop_data_2)
        current_conditions = CurrentDayConditions(
            incoming_light=light,
            min_air_temperature=min_temp,
            precipitation=rainfall,
            max_air_temperature=max_temp,
            mean_air_temperature=mean_temp,
        )
        field_data = FieldData(
            field_size=field_size,
            current_residue=residue,
            seasonal_high_water_table=high_water_table,
        )
        incorp = Field(field_data=field_data, soil=soil)
        incorp.crops = [crop_1, crop_2]

        incorp.soil.infiltration.infiltrate = MagicMock()
        incorp.soil.percolation.percolate = MagicMock()
        incorp.soil.percolation.percolate_infiltrated_water = MagicMock()
        incorp.soil.soil_erosion.erode = MagicMock()
        incorp.soil.phosphorus_cycling.cycle_phosphorus = MagicMock()
        incorp.soil.nitrogen_cycling.cycle_nitrogen = MagicMock()
        incorp.soil.carbon_cycling.cycle_carbon = MagicMock()
        incorp.soil.snow.sublimate = MagicMock()
        incorp.soil.evaporation.evaporate = MagicMock()

        incorp._determine_watering_amount = MagicMock(return_value=0)
        incorp._handle_water_in_crop_canopies = MagicMock(return_value=2.0)
        incorp._determine_potential_evapotranspiration = MagicMock(return_value=33.5)
        incorp._evaporate_from_crop_canopies = MagicMock(return_value=30.5)
        incorp._determine_total_above_ground_biomass = MagicMock(return_value=40.0)
        incorp._determine_soil_evaporation_and_sublimation_adjusted = MagicMock(return_value=10.5)
        incorp._determine_maximum_soil_evaporation = MagicMock(return_value=5.0)
        incorp._get_manure_water = MagicMock(return_value=manure_water)

        crop_1._water_dynamics.set_maximum_transpiration = MagicMock()
        crop_1._water_dynamics.cycle_water = MagicMock()
        crop_1._water_uptake.uptake = MagicMock()
        crop_2._water_dynamics.set_maximum_transpiration = MagicMock()
        crop_2._water_dynamics.cycle_water = MagicMock()
        crop_2._water_uptake.uptake = MagicMock()
        mocked_time = MagicMock(RufasTime)
        setattr(mocked_time, "current_simulation_year", 2023)
        setattr(mocked_time, "current_julian_day", 178)

        incorp._cycle_water(current_conditions, mocked_time)

        expected_total_water = rainfall + manure_water
        incorp._determine_watering_amount.assert_called_once_with(
            rainfall=rainfall,
            manure_water=manure_water,
            year=mocked_time.current_simulation_year,
            day=mocked_time.current_julian_day,
            irrigation=0.0,
        )
        incorp._handle_water_in_crop_canopies.assert_called_once_with(expected_total_water)
        incorp._determine_potential_evapotranspiration.assert_called_once_with(light, max_temp, min_temp, mean_temp)
        incorp._evaporate_from_crop_canopies.assert_called_once_with(33.5)
        incorp.soil.infiltration.infiltrate.assert_called_once_with(2.0)
        incorp.soil.percolation.percolate.assert_called_once_with(high_water_table)
        incorp.soil.percolation.percolate_infiltrated_water.assert_called_once()
        incorp.soil.soil_erosion.erode.assert_called_once_with(field_size, 0.02, residue, expected_total_water)
        incorp.soil.phosphorus_cycling.cycle_phosphorus.assert_called_once_with(2.0, runoff, field_size, mean_temp)
        incorp.soil.nitrogen_cycling.cycle_nitrogen.assert_called_once_with(field_size)
        incorp.soil.carbon_cycling.cycle_carbon.assert_called_once_with(2.0, mean_temp, field_size)
        expected_remaining_demand = 30.5
        crop_1._water_dynamics.set_maximum_transpiration.assert_called_once_with(expected_remaining_demand)
        crop_2._water_dynamics.set_maximum_transpiration.assert_called_once_with(expected_remaining_demand)
        expected_average_transpiration = 44.1 * crop_1_proportion + 39.5 * crop_2_proportion
        incorp._determine_soil_evaporation_and_sublimation_adjusted.assert_called_once_with(
            40.0,
            surface_residue,
            snow_content,
            expected_remaining_demand,
            expected_average_transpiration,
        )
        incorp.soil.snow.sublimate.assert_called_once_with(10.5)
        incorp._determine_maximum_soil_evaporation.assert_called_once_with(10.5, snow_content)
        incorp.soil.evaporation.evaporate.assert_called_once_with(5.0)
        expected_actual_evaporation = 33.5 - (expected_remaining_demand - 4.5)
        if crops_growing:
            crop_1._water_uptake.uptake.assert_called_once_with(incorp.soil.data)
            crop_1._water_dynamics.cycle_water.assert_called_once_with(expected_actual_evaporation, 3.5, 33.5)
            crop_2._water_uptake.uptake.assert_called_once_with(incorp.soil.data)
            crop_2._water_dynamics.cycle_water.assert_called_once_with(expected_actual_evaporation, 3.25, 33.5)
        else:
            assert crop_1._data.cumulative_evaporation == 0
            assert crop_1._data.cumulative_transpiration == 0
            assert crop_1._data.cumulative_potential_evapotranspiration == 0
            assert crop_2._data.cumulative_evaporation == 0
            assert crop_2._data.cumulative_transpiration == 0
            assert crop_2._data.cumulative_potential_evapotranspiration == 0


@pytest.mark.parametrize(
    "rainfall,manure_water,days_into_interval,water_deficit,watering_occurs,irrigation,old_method",
    [
        (3.4, 2.4, 3, 1.5, False, 0, False),  # No watering because water_occurs is False
        (3.1, 1.1, 5, 2.3, True, 0, False),
        # No watering because rainfall takes care of watering
        (0.2, 0.3, 5, 3.6, True, 0, False),
        # Watering occurs because water deficit has not been met
        (0.19, 0.0, 4, 2.8, True, 0, False),
        # No watering occurs because interval has not been met
        (0.2, 1.0, 5, 3.6, True, 9.24, False),
        (0.2, 0.0, 5, 3.6, False, 77.7, True),
    ],
)
def test_determine_watering_amount(
    rainfall: float,
    manure_water: float,
    days_into_interval: int,
    water_deficit: float,
    watering_occurs: float,
    irrigation: float,
    old_method: bool,
) -> None:
    """Tests that the correct amount of water to be used to water is field is calculated, and that the counters and
    totals are updated correctly."""
    mocked_time = MagicMock(RufasTime)
    setattr(mocked_time, "year", 2023)
    setattr(mocked_time, "day", 178)
    data = FieldData(
        watering_amount_in_liters=50_000,
        watering_interval=5,
        days_into_watering_interval=days_into_interval,
    )
    data.watering_amount_in_mm = 5.0
    data.watering_occurs = watering_occurs
    data.current_water_deficit = water_deficit
    incorp = Field(field_data=data)

    actual = incorp._determine_watering_amount(rainfall, manure_water, mocked_time.year, mocked_time.day, irrigation)
    if old_method:
        assert actual == irrigation
    else:
        if not watering_occurs:
            assert actual == 0.0
            assert incorp.field_data.days_into_watering_interval == days_into_interval
            assert incorp.field_data.annual_irrigation_water_use_total == 0
        elif days_into_interval == incorp.field_data.watering_interval:
            assert actual == max(0.0, water_deficit - rainfall - manure_water)
            assert incorp.field_data.days_into_watering_interval == 0
            assert incorp.field_data.current_water_deficit == 5.0
            assert incorp.field_data.annual_irrigation_water_use_total == actual
        else:
            assert actual == 0.0
            assert incorp.field_data.days_into_watering_interval == days_into_interval + 1
            assert incorp.field_data.current_water_deficit == max(0.0, water_deficit - rainfall - manure_water)
            assert incorp.field_data.annual_irrigation_water_use_total == 0


@pytest.mark.parametrize(
    "water_amount,field_name",
    [
        (0.0, "test_1"),
        (10.0, "test_2"),
        (45.3, "test_3"),
    ],
)
def test_get_manure_water(mocker: MockerFixture, water_amount: float, field_name: str) -> None:
    """Tests that manure water is correctly retrieved and logged."""
    field_data = FieldData(name=field_name, manure_water=water_amount)
    field = Field(field_data=field_data)

    with patch("RUFAS.output_manager.OutputManager.add_variable") as add_var:
        actual = field._get_manure_water()

        add_var.assert_called_once_with(
            "manure_water",
            water_amount,
            {
                "class": "Field",
                "function": "_get_manure_water",
                "suffix": f"field='{field_name}'",
                "units": MeasurementUnits.MILLIMETERS,
            },
        )

    assert actual == water_amount
    assert field.field_data.manure_water == 0.0


@pytest.mark.parametrize(
    "precipitation,canopy_capacity,first_canopy_amount,second_canopy_amount,expected_return,"
    "expected_first,expected_second",
    [
        (13, 8, 2, 4, 3, 8, 8),  # Fills both pools with some leftover
        (6, 7, 3, 2, 0, 7, 4),  # Fills one pool, puts some in second, none leftover
        (14, 5, 7, 1, 10, 7, 5),  # Removes from one pool, fills other, some leftover
        (3, 6, 8, 9, 3, 8, 9),  # Removes from both pools, lots left over
        (
            5,
            10,
            3,
            12,
            0,
            8,
            12,
        ),  # Fills one pool as much as possible, removes excess from
        # another
    ],
)
def test_handle_water_in_crop_canopies(
    precipitation: float,
    canopy_capacity: float,
    first_canopy_amount: float,
    second_canopy_amount: float,
    expected_return: float,
    expected_first: float,
    expected_second: float,
) -> None:
    """Tests that water is properly added and removed from the crop canopies of field objects."""
    with patch(
        "RUFAS.biophysical.field.crop.crop_data.CropData.water_canopy_storage_capacity",
        new_callable=PropertyMock,
        return_value=canopy_capacity,
    ):
        crop_data1 = CropData(canopy_water=first_canopy_amount, **SAMPLE_CROP_CONFIGURATION)
        crop1 = Crop(crop_data1)
        crop_data2 = CropData(canopy_water=second_canopy_amount, **SAMPLE_CROP_CONFIGURATION)
        crop2 = Crop(crop_data2)
        field = Field()
        field.crops = [crop1, crop2]

        actual = field._handle_water_in_crop_canopies(precipitation)
        assert actual == expected_return
        assert field.crops[0]._data.canopy_water == expected_first
        assert field.crops[1]._data.canopy_water == expected_second


@pytest.mark.parametrize(
    "demand,canopy_water_1,canopy_water_2,expected_demand,expected_canopy_water1," "expected_canopy_water2",
    [
        (14.5, 1.8, 2.3, 10.4, 0.0, 0.0),
        (8.6, 4.7, 4.1, 0.0, 0.0, 0.2),
        (9.5, 10.8, 5.7, 0.0, 1.3, 5.7),
    ],
)
def test_evaporate_from_crop_canopies(
    demand: float,
    canopy_water_1: float,
    canopy_water_2: float,
    expected_demand: float,
    expected_canopy_water1: float,
    expected_canopy_water2: float,
) -> None:
    """Tests that the evapotranspirative demand is correctly reduced by the amounts of water evaporated."""
    data1 = CropData(canopy_water=canopy_water_1, **SAMPLE_CROP_CONFIGURATION)
    crop1 = Crop(data1)
    data2 = CropData(canopy_water=canopy_water_2, **SAMPLE_CROP_CONFIGURATION)
    crop2 = Crop(data2)
    field = Field()
    field.crops = [crop1, crop2]

    actual_demand = field._evaporate_from_crop_canopies(demand)
    assert pytest.approx(actual_demand) == expected_demand
    assert pytest.approx(expected_canopy_water1) == field.crops[0]._data.canopy_water
    assert pytest.approx(expected_canopy_water2) == field.crops[1]._data.canopy_water


@pytest.mark.parametrize("biomasses,expected", [([30, 20, 14], 64), ([22.1], 22.1), ([], 0.0)])
def test_determine_total_above_ground_biomass(
    mock_crop_data: CropData, biomasses: List[float], expected: float
) -> None:
    """Tests that total above ground biomass on the field is correctly calculated."""
    field = Field()
    for biomass in biomasses:
        crop = Crop(crop_data=replace(mock_crop_data))
        crop._data.above_ground_biomass = biomass
        field.crops.append(crop)

    actual = field._determine_total_above_ground_biomass()
    assert actual == expected


@pytest.mark.parametrize(
    "extraterrestrial_radiation,max_temp,min_temp,avg_temp,expected_avg,expected_result",
    [
        (100, 28, 10, 14, 14, 23.869749),
        (568, 20, 14, 18, 18, 88.123445),
        (568, 20, 14, None, 17, 85.661897),
        (80, 14, 0, 8, 8, 13.663381),
        (678.0098, 26.8896, 10.3339, 18.3345, 18.3345, 176.36657),
        (678.0098, 26.8896, 10.3339, -100000, -100000, 0.0),
    ],
)
def test_potential_evapotranspiration(
    extraterrestrial_radiation: float,
    max_temp: float,
    min_temp: float,
    avg_temp: float,
    expected_avg: float,
    expected_result: float,
) -> None:
    with patch(
        "RUFAS.biophysical.field.field.field.Field._determine_latent_heat_vaporization",
        new_callable=MagicMock,
        return_value=1.3,
    ) as mocked_latent_heat:
        actual = Field._determine_potential_evapotranspiration(extraterrestrial_radiation, max_temp, min_temp, avg_temp)

        mocked_latent_heat.assert_called_once_with(expected_avg)
        assert pytest.approx(actual) == expected_result


@pytest.mark.parametrize(
    "avg_temp",
    [
        12.86878,
        0,
        (-2.586948),
        20.4486,
    ],
)
def test_determine_latent_heat_vaporization(avg_temp: float) -> None:
    observe = Field._determine_latent_heat_vaporization(avg_temp)
    expect = 2.501 - (0.002361 * avg_temp)
    assert expect == observe


@pytest.mark.parametrize(
    "above_ground_biomass,residue,snow_water,potential_evapotrans_adj,transpiration",
    [
        (800, 40, 0.3, 1.6, 0.9),  # arbitrary
        (1200, 300, 0.433, 2.4, 1.8),  # arbitrary
        (0, 800, 0.03, 0, 3.6),  # after harvest
        (800, 56, 0.84, 0.44, 0.23),  # snowy
        (0, 0, 0.22, 0.69, 0.45),  # empty field
        (400, 150, 0, 0.01, 0),  # dry conditions
        (500, 200, 0, 6.3, 4.5),  # wet conditions
        (300, 40, 2.33, 0.0, 0.0),
    ],
)
def test_determine_soil_evaporation_and_sublimation_adjusted(
    above_ground_biomass: float,
    residue: float,
    snow_water: float,
    potential_evapotrans_adj: float,
    transpiration: float,
) -> None:
    """Tests that the amount of soil evaporation and sublimation is calculated correctly."""
    with patch(
        "RUFAS.biophysical.field.field.field.Field._determine_soil_cover_index",
        new_callable=MagicMock,
        return_value=1.3,
    ) as mocked_soil_cover_index:
        actual = Field._determine_soil_evaporation_and_sublimation_adjusted(
            above_ground_biomass,
            residue,
            snow_water,
            potential_evapotrans_adj,
            transpiration,
        )
        if potential_evapotrans_adj == transpiration == 0.0:
            expected = 0.0
            mocked_soil_cover_index.assert_not_called()
        else:
            soil_evaporation = potential_evapotrans_adj * 1.3
            reduced_soil_evaporation = (soil_evaporation * potential_evapotrans_adj) / (
                soil_evaporation + transpiration
            )
            expected = min(soil_evaporation, reduced_soil_evaporation)
            mocked_soil_cover_index.assert_called_once_with(above_ground_biomass, residue, snow_water)

        assert actual == expected


@pytest.mark.parametrize(
    "soil_evaporation_adj,snow_water_content",
    [(1.3, 3.2), (0, 0), (1.3, 0.4), (1.8954, 0)],
)
def test_determine_maximum_soil_evaporation(soil_evaporation_adj: float, snow_water_content: float) -> None:
    observe = Field._determine_maximum_soil_evaporation(soil_evaporation_adj, snow_water_content)
    if snow_water_content > soil_evaporation_adj:
        assert 0 == observe
    else:
        assert (soil_evaporation_adj - snow_water_content) == observe


@pytest.mark.parametrize(
    "above_ground_biomass,residue,snow_water",
    [
        (400, 65, 0.3),
        (800, 120, 0),
        (0, 0, 0),
        (1250, 800, 0.4999),
        (990, 200, 0.338),
        (400, 30, 0.51),
    ],
)
def test_determine_soil_cover_index(above_ground_biomass: float, residue: float, snow_water: float) -> None:
    """Tests that the soil cover index is correctly calculated."""
    if snow_water > 0.5:
        expect = 0.5
    else:
        expect = exp((-0.00005) * (above_ground_biomass + residue))
    observe = Field._determine_soil_cover_index(above_ground_biomass, residue, snow_water)
    assert expect == observe


def test_annual_reset() -> None:
    """Tests that all annual reset subroutines are called properly"""
    field = Field()
    field.soil.data.do_annual_reset = MagicMock()
    field.field_data.perform_annual_field_reset = MagicMock()

    field.perform_annual_reset()

    field.soil.data.do_annual_reset.assert_called_once()
    field.field_data.perform_annual_field_reset.assert_called_once()


@pytest.mark.parametrize(
    "events, day, year, not_today, is_today",
    [
        (
            [
                TillageEvent(10, 0.5, 0.3, TillageImplement.CULTIVATOR, 1997, 7),
                TillageEvent(10, 0.5, 0.3, TillageImplement.CULTIVATOR, 1998, 7),
                TillageEvent(10, 0.5, 0.3, TillageImplement.CULTIVATOR, 1999, 7),
            ],
            7,
            1998,
            [
                TillageEvent(10, 0.5, 0.3, TillageImplement.CULTIVATOR, 1999, 7),
            ],
            [
                TillageEvent(
                    10,
                    0.5,
                    0.3,
                    TillageImplement.CULTIVATOR,
                    1998,
                    7,
                )
            ],
        ),
        ([], 7, 1998, [], []),
        (
            [
                TillageEvent(
                    10,
                    0.5,
                    0.3,
                    TillageImplement.CULTIVATOR,
                    1997,
                    7,
                ),
                TillageEvent(
                    10,
                    0.5,
                    0.3,
                    TillageImplement.CULTIVATOR,
                    1999,
                    7,
                ),
                TillageEvent(
                    10,
                    0.5,
                    0.3,
                    TillageImplement.CULTIVATOR,
                    2023,
                    7,
                ),
            ],
            7,
            1998,
            [
                TillageEvent(
                    10,
                    0.5,
                    0.3,
                    TillageImplement.CULTIVATOR,
                    1999,
                    7,
                ),
                TillageEvent(
                    10,
                    0.5,
                    0.3,
                    TillageImplement.CULTIVATOR,
                    2023,
                    7,
                ),
            ],
            [],
        ),
        (
            [
                TillageEvent(
                    7,
                    0.5,
                    0.3,
                    TillageImplement.CULTIVATOR,
                    1998,
                    7,
                ),
                TillageEvent(
                    10,
                    0.5,
                    0.4,
                    TillageImplement.CULTIVATOR,
                    1998,
                    7,
                ),
                TillageEvent(
                    5,
                    0.5,
                    0.3,
                    TillageImplement.CULTIVATOR,
                    1998,
                    7,
                ),
            ],
            7,
            1998,
            [],
            [
                TillageEvent(
                    7,
                    0.5,
                    0.3,
                    TillageImplement.CULTIVATOR,
                    1998,
                    7,
                ),
                TillageEvent(
                    10,
                    0.5,
                    0.4,
                    TillageImplement.CULTIVATOR,
                    1998,
                    7,
                ),
                TillageEvent(
                    5,
                    0.5,
                    0.3,
                    TillageImplement.CULTIVATOR,
                    1998,
                    7,
                ),
            ],
        ),
    ],
)
def test_check_tillage_schedule(
    events: List[TillageEvent],
    day: int,
    year: int,
    not_today: List[TillageEvent],
    is_today: List[TillageEvent],
) -> None:
    mocked_time = MagicMock(RufasTime)
    setattr(mocked_time, "current_calendar_year", year)
    setattr(mocked_time, "current_julian_day", day)
    setattr(mocked_time, "current_date", RufasTime.convert_year_jday_to_date(year, day))

    field = Field(tillage_events=events)
    todays_count = len(is_today)
    field.tiller.till_soil = MagicMock()
    field._check_tillage_schedule(mocked_time)
    assert field.tillage_events == not_today

    assert field.tiller.till_soil.call_count == todays_count


# --- Test FieldData methods ---
@pytest.mark.parametrize(
    "liters,area,expected",
    [(100, 2.3, 0.004347826086956522), (356, 4.556, 0.00781387181738367), (60, 1.8, 0.0033333333333333335)],
)
def test_liters_to_millimeters(liters: float, area: float, expected: float) -> None:
    """Tests that the conversion from liters for evenly distributed millimeters is performed correctly."""
    actual = FieldData.convert_liters_to_millimeters(liters, area)
    assert actual == expected


@pytest.mark.parametrize(
    "latitude,min_daylength,watering_amount,watering_interval",
    [
        (45.66, 12.5, 2000, 3),
        (37.445, 9.88, 7500, 7),
        (50.667, 10.334, 0, 5),
        (49.551, 12.65, 3500, 0),
    ],
)
def test_field_data_initialization(
    latitude: float,
    min_daylength: float,
    watering_amount: float,
    watering_interval: int,
) -> None:
    """Tests that FieldData objects are initialized correctly."""
    Dormancy.find_dormancy_threshold = MagicMock(return_value=14.5)
    Dormancy.find_threshold_daylength = MagicMock(return_value=10.22)
    FieldData.convert_liters_to_millimeters = MagicMock(return_value=0.8)

    data = FieldData(
        field_size=3,
        absolute_latitude=latitude,
        minimum_daylength=min_daylength,
        watering_amount_in_liters=watering_amount,
        watering_interval=watering_interval,
    )

    Dormancy.find_dormancy_threshold.assert_called_once_with(latitude)
    Dormancy.find_threshold_daylength.assert_called_once_with(min_daylength, 14.5)
    assert data.dormancy_threshold == 14.5
    assert data.dormancy_threshold_daylength == 10.22
    if (
        watering_amount is not None
        and watering_amount != 0.0
        and watering_interval is not None
        and watering_interval != 0
    ):
        FieldData.convert_liters_to_millimeters.assert_called_once_with(watering_amount, 3)
        assert data.watering_amount_in_mm == 0.8
        assert data.current_water_deficit == 0.8
        assert data.watering_occurs
    else:
        FieldData.convert_liters_to_millimeters.assert_not_called()
        assert data.watering_amount_in_mm == 0
        assert data.current_water_deficit == 0
        assert not data.watering_occurs


@pytest.mark.parametrize("watering_amount,interval", [(-1300, 13), (2000, -3)])
def test_error_field_data_initialization(watering_amount: float, interval: int) -> None:
    """Tests that errors are correctly raised when FieldData is initialized with invalid values."""
    with pytest.raises(Exception) as e:
        FieldData(watering_amount_in_liters=watering_amount, watering_interval=interval)
    if watering_amount < 0:
        assert f"Expected watering amount to be >= 0, received '{watering_amount}'." == str(e.value)
    elif interval < 0:
        assert f"Expected watering interval to be >= 0, received '{interval}'." == str(e.value)


@pytest.mark.parametrize(
    "field_name,field_size,day,year,watering_amount,expected_info_map,expected_value",
    [
        (
            "name_1",
            100,
            120,
            1993,
            135.6,
            {
                "suffix": "field='name_1'",
                "year": 1993,
                "day": 120,
                "field_size": 100,
                "units": MeasurementUnits.MILLIMETERS.value,
            },
            135.6,
        ),
        (
            "name_2",
            14.65,
            3,
            1996,
            1.2,
            {
                "suffix": "field='name_2'",
                "year": 1996,
                "day": 3,
                "field_size": 14.65,
                "units": MeasurementUnits.MILLIMETERS.value,
            },
            1.2,
        ),
        (
            "name_2",
            14.65,
            48,
            2023,
            1.2,
            {
                "suffix": "field='name_2'",
                "year": 2023,
                "day": 48,
                "field_size": 14.65,
                "units": MeasurementUnits.MILLIMETERS.value,
            },
            1.2,
        ),
    ],
)
def test_record_field_watering(
    field_name: str,
    field_size: float,
    day: int,
    year: int,
    watering_amount: float,
    expected_info_map: dict[str, Any],
    expected_value: dict[str, Any],
) -> None:
    field = Field(
        field_data=FieldData(name=field_name, field_size=field_size),
    )
    field._record_field_watering(year=year, day=day, watering_amount=watering_amount)

    actual = field.om.variables_pool[f"Field._record_field_watering.field_watering.field='{field_name}'"]
    assert actual["info_maps"].__contains__(expected_info_map)
    assert actual["values"].__contains__(expected_value)


@pytest.mark.parametrize("annual_irrigation_water_use_total,expected", [(1500, 0), (063.25, 0), (0, 0)])
def test_field_data_perform_annual_field_reset(annual_irrigation_water_use_total: float, expected: float) -> None:
    """Tests that annual variable was reset correctly."""
    data = FieldData(annual_irrigation_water_use_total=annual_irrigation_water_use_total)
    data.perform_annual_field_reset()
    assert expected == data.annual_irrigation_water_use_total

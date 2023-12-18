from math import exp
from typing import List, Dict
from unittest.mock import MagicMock, PropertyMock, patch, call
import pytest
from RUFAS.routines.field.crop.crop import Crop
from RUFAS.routines.field.crop.crop_data import CropData
from RUFAS.routines.field.crop.harvest_operations import HarvestOperation
from RUFAS.routines.field.crop.species_data_factory import CropSpecies
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.routines.field.manager.events import Event, PlantingEvent, HarvestEvent, FertilizerEvent, ManureEvent
from RUFAS.routines.field.soil.soil import Soil
from RUFAS.routines.field.soil.soil_data import SoilData
from RUFAS.routines.field.field.field import Field
from RUFAS.routines.field.field.field_data import FieldData
from RUFAS.routines.field.crop.dormancy import Dormancy
from RUFAS.routines.field.crop_and_soil_constants import LITERS_TO_CUBIC_MILLIMETERS, HECTARES_TO_SQUARE_MILLIMETERS
from RUFAS.time import Time
from RUFAS.routines.field.manager.events import TillageEvent
from RUFAS.output_manager import OutputManager
from RUFAS.routines.manure.manure_manager import ManureManager
from RUFAS.routines.manure.manure_nutrients.nutrient_request_results import NutrientRequestResults
from RUFAS.routines.manure.manure_nutrients.nutrient_request import NutrientRequest

om = OutputManager()


@pytest.mark.parametrize("manure_manager,should_fail", [
    (MagicMock(ManureManager), False),
    (None, True)
])
def test_init(manure_manager: ManureManager, should_fail: bool) -> None:
    """Tests that Field initialization fails when passed invalid parameters."""
    if should_fail:
        with pytest.raises(ValueError, match="Manure manager cannot be None."):
            Field(manure_manager=manure_manager)
    else:
        Field(manure_manager=manure_manager)
        assert True


def test_manage_field() -> None:
    """Tests that all subroutines are correctly called by the main routine in field."""
    field = Field(manure_manager=MagicMock(ManureManager))
    field._check_fertilizer_application_schedule = MagicMock()
    field._check_manure_application_schedule = MagicMock()
    field._check_tillage_schedule = MagicMock()
    field._execute_daily_processes = MagicMock()
    field._assess_dormancy = MagicMock()
    field._check_crop_planting_schedule = MagicMock()
    field._check_crop_harvest_schedule = MagicMock()
    field._remove_dead_crops = MagicMock()
    field._reset_crop_field_coverage_fractions = MagicMock()
    mocked_time = MagicMock(Time)
    mocked_weather = MagicMock(CurrentDayConditions)
    setattr(mocked_weather, "daylength", 12)
    setattr(mocked_weather, "rainfall", 3.0)

    field.manage_field(mocked_time, mocked_weather)

    field._check_fertilizer_application_schedule.assert_called_once_with(mocked_time)
    field._check_manure_application_schedule.assert_called_once_with(mocked_time)
    field._check_tillage_schedule.assert_called_once_with(mocked_time)
    field._execute_daily_processes.assert_called_once_with(mocked_weather, mocked_time)
    field._assess_dormancy.assert_called_once_with(12, 3.0)
    field._check_crop_planting_schedule.assert_called_once_with(mocked_time)
    field._check_crop_harvest_schedule.assert_called_once_with(mocked_time, mocked_weather)
    field._remove_dead_crops.assert_called_once()
    field._reset_crop_field_coverage_fractions.assert_called_once()


@pytest.mark.parametrize("all_events,events_remaining,events_occurring_today", [
    ([PlantingEvent("test_1", 1996, 120, False), PlantingEvent("test_2", 1996, 120, False),
      PlantingEvent("test_3", 1996, 240, False), PlantingEvent("test_4", 1997, 125, False)],
     [PlantingEvent("test_3", 1996, 240, False), PlantingEvent("test_4", 1997, 125, False)],
     [PlantingEvent("test_1", 1996, 120, False), PlantingEvent("test_2", 1996, 120, False)]),
    ([PlantingEvent("crop_1", 1995, 100, True), PlantingEvent("crop_2", 1995, 100, False),
      PlantingEvent("crop_3", 1995, 100, False)], [],
     [PlantingEvent("crop_1", 1995, 100, True),
      PlantingEvent("crop_2", 1995, 100, False), PlantingEvent("crop_3", 1995, 100, False)]),
    ([PlantingEvent("not_today_1", 2000, 100, False), PlantingEvent("not_today_2", 2000, 250, True),
      PlantingEvent("not_today_3", 2001, 200, True)],
     [PlantingEvent("not_today_1", 2000, 100, False), PlantingEvent("not_today_2", 2000, 250, True),
      PlantingEvent("not_today_3", 2001, 200, True)], []),
    ([], [], [])
])
def test_check_crop_planting_schedule(all_events: List[PlantingEvent], events_remaining: List[PlantingEvent],
                                      events_occurring_today: List[PlantingEvent]) -> None:
    """
    Tests that the planting schedule is updated correctly and that planting events are executed correctly. This test
    contains four cases: some planting events occur on the current day, all planting events occur on the current day,
    no planting events occur on the current day, and no planting events left.
    """
    field = Field(plantings=all_events, manure_manager=MagicMock(ManureManager))
    field._filter_events = MagicMock(return_value=(events_remaining, events_occurring_today))

    field._plant_crop = MagicMock()
    time = MagicMock(Time)
    expected_create_and_update_events_calls = [call(all_events, time)]

    field._check_crop_planting_schedule(time)

    field._filter_events.assert_has_calls(expected_create_and_update_events_calls)
    assert field._plant_crop.call_count == len(events_occurring_today)
    assert field.planting_events == events_remaining


@pytest.mark.parametrize("events,remaining_events,current_events", [
    ([FertilizerEvent("mix_1", 100, 20, 1993, 75, 0, 1.0), FertilizerEvent("mix_2", 20, 20, 1993, 75, 0, 1.0),
      FertilizerEvent("mix_3", 15, 15, 1993, 75, 0, 1.0)], [], [FertilizerEvent("mix_1", 100, 20, 1993, 75, 0, 1.0),
                                                                FertilizerEvent("mix_2", 20, 20, 1993, 75, 0, 1.0),
                                                                FertilizerEvent("mix_3", 15, 15, 1993, 75, 0, 1.0)]),
    ([FertilizerEvent("mix_1", 150, 20, 1992, 80, 0, 1.0), FertilizerEvent("mix_1", 25, 5, 1992, 250, 0, 1.0),
      FertilizerEvent("mix_1", 100, 50, 1993, 80, 0, 1.0)], [FertilizerEvent("mix_1", 25, 5, 1992, 250, 0, 1.0),
                                                             FertilizerEvent("mix_1", 100, 50, 1993, 80, 0, 1.0)],
     [FertilizerEvent("mix_1", 150, 20, 1992, 80, 0, 1.0)]),
    ([FertilizerEvent("mix_1", 50, 10, 1998, 90, 0, 1.0), FertilizerEvent("mix_1", 50, 10, 1999, 90, 0, 1.0),
      FertilizerEvent("mix_1", 50, 10, 2000, 90, 0, 1.0)], [FertilizerEvent("mix_1", 50, 10, 1998, 90, 0, 1.0),
                                                            FertilizerEvent("mix_1", 50, 10, 1999, 90, 0, 1.0),
                                                            FertilizerEvent("mix_1", 50, 10, 2000, 90, 0, 1.0)], [])
])
def test_check_fertilizer_application_schedule(events: List[FertilizerEvent], remaining_events: List[FertilizerEvent],
                                               current_events: List[FertilizerEvent]) -> None:
    """Tests that fertilizer events that occur on the current day are properly selected and executed."""
    field = Field(fertilizer_events=events, manure_manager=MagicMock(ManureManager))
    field._filter_events = MagicMock(return_value=(remaining_events, current_events))
    field._execute_fertilizer_application = MagicMock()
    mocked_time = MagicMock(Time)
    setattr(mocked_time, "calendar_year", 2000)
    setattr(mocked_time, "day", 100)

    field._check_fertilizer_application_schedule(mocked_time)

    expected_execution_calls = []
    for event in current_events:
        expected_execution_calls.append(call(event.mix_name, event.nitrogen_mass, event.phosphorus_mass, event.depth,
                                             event.surface_remainder_fraction, event.year, event.day))
    field._filter_events.assert_called_once_with(events, mocked_time)
    field._execute_fertilizer_application.assert_has_calls(expected_execution_calls)


@pytest.mark.parametrize("events,remaining_events,current_events", [
    ([ManureEvent(1991, 120, 100, 20, 0.8, 0.0, 1.0), ManureEvent(1992, 120, 100, 20, 0.8, 0.0, 1.0),
      ManureEvent(1993, 120, 100, 20, 0.8, 0.0, 1.0)],
     [ManureEvent(1992, 120, 100, 20, 0.8, 0.0, 1.0), ManureEvent(1993, 120, 100, 20, 0.8, 0.0, 1.0)],
     [ManureEvent(1991, 120, 100, 20, 0.8, 0.0, 1.0)]),
    ([ManureEvent(1991, 125, 100, 20, 0.8, 0.0, 1.0), ManureEvent(1992, 125, 100, 20, 0.8, 0.0, 1.0),
      ManureEvent(1993, 125, 100, 20, 0.8, 0.0, 1.0)],
     [ManureEvent(1991, 125, 100, 20, 0.8, 0.0, 1.0), ManureEvent(1992, 125, 100, 20, 0.8, 0.0, 1.0),
      ManureEvent(1993, 125, 100, 20, 0.8, 0.0, 1.0)], []),
    ([ManureEvent(1991, 120, 100, 20, 0.8, 0.0, 1.0), ManureEvent(1991, 120, 90, 20, 0.8, 0.0, 1.0),
      ManureEvent(1991, 120, 80, 40, 0.8, 0.0, 1.0)], [],
     [ManureEvent(1991, 120, 100, 20, 0.8, 0.0, 1.0), ManureEvent(1991, 120, 90, 20, 0.8, 0.0, 1.0),
      ManureEvent(1991, 120, 80, 40, 0.8, 0.0, 1.0)])
])
def test_check_manure_application_schedule(events: List[ManureEvent], remaining_events: List[ManureEvent],
                                           current_events: List[ManureEvent]) -> None:
    """Tests that ManureEvents are correctly checked for and executed when scheduled."""
    field = Field(manure_events=events, manure_manager=MagicMock(ManureManager))
    field._filter_events = MagicMock(return_value=(remaining_events, current_events))
    field._execute_manure_application = MagicMock()
    mocked_time = MagicMock(Time)
    setattr(mocked_time, "calendar_year", 1991)
    setattr(mocked_time, "day", 120)

    field._check_manure_application_schedule(mocked_time)

    expected_execution_calls = []
    for event in current_events:
        expected_execution_calls.append(call(event.nitrogen_mass, event.phosphorus_mass, event.field_coverage,
                                             event.application_depth, event.surface_remainder_fraction, event.year,
                                             event.day))
    field._filter_events.assert_called_once_with(events, mocked_time)
    assert field.manure_events == remaining_events
    field._execute_manure_application.assert_has_calls(expected_execution_calls)


@pytest.mark.parametrize("year,day,all_harvest_events,current_harvest_events", [
    (1990, 240,
     [HarvestEvent("corn", 1990, 240, "no_kill"), HarvestEvent("corn", 1990, 255, "default")],
     [HarvestEvent("cover", 1990, 240, "default")]),
    (1991, 126,
     [HarvestEvent("corn", 1991, 240, "default"), HarvestEvent("cover", 1991, 260, "default")],
     []),
    (1992, 230, [HarvestEvent("corn", 1992, 230, "default"),
                 HarvestEvent("cover_1", 1992, 230, "default"),
                 HarvestEvent("cover_2", 1992, 230, "default")],
     [HarvestEvent("corn", 1992, 230, "default"),
      HarvestEvent("cover_1", 1992, 230, "default"),
      HarvestEvent("cover_2", 1992, 230, "default")]),
    (1993, 145, [], [])
])
def test_check_crop_harvest_schedule(year: int, day: int, all_harvest_events: List[HarvestEvent],
                                     current_harvest_events: List[HarvestEvent]) -> None:
    """Tests that the schedule of crop harvests is determined correctly for any given day."""
    field = Field(harvestings=all_harvest_events, manure_manager=MagicMock(ManureManager))

    mocked_time = MagicMock(Time)
    setattr(mocked_time, "calendar_year", year)
    setattr(mocked_time, "day", day)
    mock_conditions = MagicMock(CurrentDayConditions)
    remaining_harvest_events = [events for events in all_harvest_events if events not in current_harvest_events]
    field._filter_events = MagicMock(return_value=(remaining_harvest_events, current_harvest_events))
    field._harvest_crop = MagicMock()
    field._harvest_heat_scheduled_crops = MagicMock()

    harvest_crop_calls = []
    for event in current_harvest_events:
        new_call = call(event.crop_reference, event.operation, mocked_time, mock_conditions)
        harvest_crop_calls.append(new_call)

    field._check_crop_harvest_schedule(mocked_time, mock_conditions)

    field._filter_events.assert_called_once_with(all_harvest_events, mocked_time)
    field._harvest_crop.assert_has_calls(harvest_crop_calls)
    field._harvest_heat_scheduled_crops.assert_called_once()


@pytest.mark.parametrize("crop_num,heat_scheduled,expected_harvested,expected_harvest_count", [
    (5, [True, False, True, True, False], [True, False, False, True, False], 2),
    (2, [True, True], [False, True], 1),
    (2, [False, False], [False, False], 0),
    (0, [], [], 0)
])
def test_harvest_heat_scheduled_crops(crop_num: int, heat_scheduled: List[bool],
                                      expected_harvested: List[bool], expected_harvest_count: int) -> None:
    """Tests that all crops which are set to be harvested based on heat level are."""
    crops = []
    for index in range(crop_num):
        mock_data = MagicMock(CropData)
        crops.append(MagicMock(Crop(mock_data)))
        if heat_scheduled[index]:
            crops[index].data.use_heat_scheduling = True
        else:
            crops[index].data.use_heat_scheduling = False
        crops[index].data.harvest_heat_fraction = 1.0
        if expected_harvested[index]:
            crops[index].data.heat_fraction = crops[index].data.harvest_heat_fraction
        else:
            crops[index].data.heat_fraction = 0.0
        crops[index].crop_management.manage_harvest = MagicMock()

    field = Field(manure_manager=MagicMock(ManureManager))
    field.crops = crops
    with patch.object(field.soil.carbon_cycling.residue_partition, "add_residue_to_pools", new_callable=MagicMock) \
            as add_residue:
        field._harvest_heat_scheduled_crops(10.0)

    for index in range(len(crops)):
        if expected_harvested[index]:
            crops[index].crop_management.manage_harvest.assert_called_once_with(HarvestOperation.HARVEST_NOKILL)
        else:
            crops[index].crop_management.manage_harvest.assert_not_called()
    assert add_residue.call_count == expected_harvest_count


@pytest.mark.parametrize("events,year,day,expected_remaining,expected_current", [
    ([Event(1990, 120), Event(1990, 200), Event(1993, 100)], 1990, 120,
     [Event(1990, 200), Event(1993, 100)], [Event(1990, 120)]),
    ([PlantingEvent("corn", 1993, 120, False), PlantingEvent("corn_supplement", 1993, 120, True),
      PlantingEvent("cover_crop", 1993, 245, False)], 1993, 120, [PlantingEvent("cover_crop", 1993, 245, False)],
     [PlantingEvent("corn", 1993, 120, False), PlantingEvent("corn_supplement", 1993, 120, True)]),
    ([HarvestEvent("corn_1", 1999, 240, "default"), HarvestEvent("corn_1", 2000, 240, "default"),
      HarvestEvent("alfalfa_2", 2001, 240, "default")], 1999, 200,
     [HarvestEvent("corn_1", 1999, 240, "default"), HarvestEvent("corn_1", 2000, 240, "default"),
      HarvestEvent("alfalfa_2", 2001, 240, "default")], []),
    ([], 1993, 140, [], [])
])
def test_filter_events(events: List[Event], year: int, day: int, expected_remaining: List[Event],
                       expected_current: List[Event]) -> None:
    """Tests that list of events are properly checked and have current events correctly removed from them."""
    mocked_time = MagicMock(Time)
    setattr(mocked_time, "calendar_year", year)
    setattr(mocked_time, "day", day)

    actual = Field._filter_events(events, mocked_time)
    assert actual[0] == expected_remaining
    assert actual[1] == expected_current


@pytest.mark.parametrize("crop_reference,heat_scheduled,custom_crop_specs,is_supported,year,day", [
    ("corn_silage", False, None, True, 1990, 120),
    ("custom_alfalfa", False, {"custom_alfalfa": {"species": "alfalfa", "minimum_temperature": 3.0}}, False, 1992, 115),
    ("alien_crop", True, {"custom_corn": {"species": "corn", "is_nitrogen_fixer": True},
                          "alien_crop": {"species": "halo_alien_corn", "minimum_temperature": -60}}, False, 2000, 110)
])
def test_plant_crop(crop_reference: str, heat_scheduled: bool, custom_crop_specs: Dict, is_supported: bool, year: int,
                    day: int) -> None:
    """Tests that a new Crop instance is properly created and added to a field."""
    field_data = FieldData(name="test", field_size=1.3)
    field = Field(field_data=field_data, custom_crop_specifications=custom_crop_specs,
                  manure_manager=MagicMock(ManureManager))
    mocked_time = MagicMock(Time)
    setattr(mocked_time, "calendar_year", year)
    setattr(mocked_time, "day", day)
    field._record_planting = MagicMock()

    field._plant_crop(crop_reference, heat_scheduled, mocked_time)

    if is_supported:
        expected_crop = field._make_supported_crop(crop_reference)
    else:
        expected_crop = field._make_crop_from_config_dict(custom_crop_specs.get(crop_reference))
    expected_crop.data.use_heat_scheduling = heat_scheduled
    expected_crop.data.id = crop_reference

    assert field.crops[0].data.id == expected_crop.data.id
    assert field.crops[0].data.use_heat_scheduling == expected_crop.data.use_heat_scheduling
    assert field.crops[0].data.species == expected_crop.data.species
    assert field.crops[0].data.planting_year == year
    assert field.crops[0].data.planting_day == day
    field._record_planting.assert_called_once_with(crop_reference, heat_scheduled, expected_crop.data.species,
                                                   year, day)


@pytest.mark.parametrize("crop_reference,heat_scheduled,species,year,day,field_name,field_size,expected_info_map,"
                         "expected_value", [
                             ("ref_1", False, "species_1", 1993, 100, "name_1", 1.3,
                              {"prefix": "field='name_1'", "field_size": 1.3, "species": "species_1"},
                              {"crop_reference": "ref_1", "heat_scheduled_harvest": False,
                               "date": {"year": 1993, "day": 100}}),
                             ("ref_2", True, "custom_alien_species", 1996, 120, "name_2", 2.55,
                              {"prefix": "field='name_2'", "field_size": 2.55, "species": "custom_alien_species"},
                              {"crop_reference": "ref_2", "heat_scheduled_harvest": True,
                               "date": {"year": 1996, "day": 120}}),
                             ("ref_3", False, "custom_corn", 2008, 122, "name_3", 0.95,
                              {"prefix": "field='name_3'", "field_size": 0.95, "species": "custom_corn"},
                              {"crop_reference": "ref_3", "heat_scheduled_harvest": False,
                               "date": {"year": 2008, "day": 122}})
                         ])
def test_record_planting(crop_reference: str, heat_scheduled: bool, species: str, year: int, day: int, field_name: str,
                         field_size: float, expected_info_map: Dict, expected_value: Dict) -> None:
    """Tests that crop plantings are correctly recorded to the OutputManager."""
    field = Field(field_data=FieldData(name=field_name, field_size=field_size), manure_manager=MagicMock(ManureManager))
    field._record_planting(crop_reference, heat_scheduled, species, year, day)

    actual = om.variables_pool[f"field='{field_name}'.crop_planting"]
    assert actual["info_maps"].__contains__(expected_info_map)
    assert actual["values"].__contains__(expected_value)


@pytest.mark.parametrize("field_name,crop_reference,custom_crop_specs,expected", [
    ("test_field_1", "halo_alien_alfalfa", {"halo_alien_winter_wheat": {"species": "halo_alien_winter_wheat",
                                                                        "minimum_temperature": -75},
                                            "halo_alien_corn": {"species": "halo_alien_corn",
                                                                "minimum_temperature": -60}},
     "'test_field_1': expected to have crop specification for 'halo_alien_alfalfa', received specifications for "
     "'('halo_alien_winter_wheat', 'halo_alien_corn')' crop types."),
    ("test_field_2", "halo_alien_durum_wheat", None, "'test_field_2': expected to have crop specification for "
                                                     "'halo_alien_durum_wheat', received specifications for '()' crop "
                                                     "types.")
])
def test_plant_crop_error(field_name: str, crop_reference: str, custom_crop_specs: Dict, expected: str) -> None:
    """Tests that errors are correctly raised when a crop specification for a requested planting is not present."""
    field = Field(custom_crop_specifications=custom_crop_specs, manure_manager=MagicMock(ManureManager))
    field.field_data.name = field_name
    mocked_time = MagicMock(Time)
    with pytest.raises(KeyError) as e:
        field._plant_crop(crop_reference, True, mocked_time)
    assert expected in str(e.value)


@pytest.mark.parametrize("crop_reference,harvest_op,field_name,field_size,rainfall,expected_operation", [
    ("test_1", "default", "field_1", 1.4, 0.0, HarvestOperation.HARVEST),
    ("test_2", "no_kill", "field_2", 2.33, 10.3, HarvestOperation.HARVEST_NOKILL),
])
def test_harvest_crop(crop_reference: str, harvest_op: str, field_name: str, field_size: float, rainfall: float,
                      expected_operation: HarvestOperation) -> None:
    """Tests that crops are harvested correctly."""
    harvest_crop = Crop()
    harvest_crop.data.id = crop_reference
    other_crop_1 = Crop()
    other_crop_2 = Crop()
    other_crop_1.data.id, other_crop_2.data.id = "not this crop", "not this crop"
    field_data = FieldData(name=field_name, field_size=field_size)
    field = Field(field_data=field_data, manure_manager=MagicMock(ManureManager))
    field.crops = [harvest_crop, other_crop_1, other_crop_2]
    for crop in field.crops:
        crop.crop_management.manage_harvest = MagicMock()
    mocked_time = MagicMock(Time)
    setattr(mocked_time, "day", 100)
    setattr(mocked_time, "calendar_year", 1995)
    mock_conditions = MagicMock(CurrentDayConditions)
    mock_conditions.rainfall == rainfall

    with patch.object(field.soil.carbon_cycling.residue_partition, "add_residue_to_pools", new_callable=MagicMock) \
            as add_residue:
        field._harvest_crop(crop_reference, harvest_op, mocked_time, mock_conditions)

    for crop in field.crops:
        if crop.data.id == "not this crop":
            crop.crop_management.manage_harvest.assert_not_called()
        else:
            crop.crop_management.manage_harvest.assert_called_once_with(expected_operation, field_name, field_size,
                                                                        1995, 100, field.soil.data)
    assert add_residue.call_count == 1


@pytest.mark.parametrize("crops,expected_info_map,expected_message", [
    ([Crop(), Crop()], {"prefix": "field_name:'test'", "date": {"day": 200, "year": 2000},
                        "timestamp": "00-Jan-1970_Thu_00-00-00"},
     "Multiple crops to be harvested by single HarvestEvent."),
    ([], {"prefix": "field_name:'test'", "date": {"day": 200, "year": 2000}, "timestamp": "00-Jan-1970_Thu_00-00-00"},
     "No crop found to be harvested by a HarvestEvent.")
])
def test_harvest_crop_warnings(crops: List[Crop], expected_info_map: Dict, expected_message: str) -> None:
    """Tests that warnings are raised correctly to the OutputManager."""
    with patch.object(om, "_get_timestamp") as mocked_timestamp:
        for crop in crops:
            crop.data.id = "test"
            crop.crop_management.manage_harvest = MagicMock()
        field = Field(manure_manager=MagicMock(ManureManager))
        field.field_data.name = "test"
        field.crops = crops
        mocked_time = MagicMock(Time)
        setattr(mocked_time, "day", 200)
        setattr(mocked_time, "calendar_year", 2000)
        mocked_timestamp.return_value = "00-Jan-1970_Thu_00-00-00"
        mock_conditions = MagicMock(CurrentDayConditions)
        mock_conditions.rainfall = 11.0

        with patch.object(field.soil.carbon_cycling.residue_partition, "add_residue_to_pools", new_callable=MagicMock) \
                as add_residue:
            field._harvest_crop("test", "default", mocked_time, mock_conditions)

        for crop in crops:
            crop.crop_management.manage_harvest.assert_called_once_with(HarvestOperation.HARVEST, "test", 1.0, 2000,
                                                                        200, field.soil.data)
        assert add_residue.call_count == len(crops)
        actual = om.warnings_pool["field_name:'test'.harvest_warning"]
        assert actual['info_maps'].__contains__(expected_info_map)
        assert actual['values'].__contains__(expected_message)


def test_remove_dead_crops() -> None:
    """
    Tests that dead crops are removed from a field correctly.
    This test contains four cases: there are no crops in the field, some crops in the field are dead, no crops in the
    field are dead, and all crops in the field are dead.
    """
    field_1 = Field(manure_manager=MagicMock(ManureManager))
    field_1._remove_dead_crops()
    assert field_1.crops == []

    field_2 = Field(manure_manager=MagicMock(ManureManager))
    crop_1 = Crop()
    crop_1.data.is_alive = False
    crop_2 = Crop()
    crop_3 = Crop()
    field_2.crops = [crop_1, crop_2, crop_3]
    field_2._remove_dead_crops()
    assert field_2.crops == [crop_2, crop_3]

    field_3 = Field(manure_manager=MagicMock(ManureManager))
    crop_4 = Crop()
    crop_5 = Crop()
    crop_6 = Crop()
    field_3.crops = [crop_4, crop_5, crop_6]
    field_3._remove_dead_crops()
    assert field_3.crops == [crop_4, crop_5, crop_6]

    field_4 = Field(manure_manager=MagicMock(ManureManager))
    crop_7 = Crop()
    crop_8 = Crop()
    field_4.crops = [crop_7, crop_8]
    field_4._remove_dead_crops()
    assert field_4.crops == [crop_7, crop_8]


@pytest.mark.parametrize("crop_list,expected_field_proportion", [
    ([Crop(), Crop(), Crop()], (1 / 3)),
    ([Crop()], 1.0),
    ([Crop(), Crop(), Crop(), Crop()], 0.25),
    ([], None)
])
def test_reset_crop_field_coverage_fractions(crop_list: List[Crop], expected_field_proportion: float) -> None:
    """Tests that crops in a field correctly have their proportion reset when there are other crops present."""
    field = Field(manure_manager=MagicMock(ManureManager))
    field.crops = crop_list
    field._reset_crop_field_coverage_fractions()
    for crop in field.crops:
        assert crop.data.field_proportion == expected_field_proportion


@pytest.mark.parametrize("daylength,threshold_daylength", [
    (14, 8),
    (17.20948239, 9.19183294),
    (7.293485893, 8.234850920),
])
def test_start_dormancy(daylength: float, threshold_daylength: float) -> None:
    """Tests that each crop's dormancy method is called."""
    crop = Crop()
    field = Field(manure_manager=MagicMock(ManureManager))
    field.field_data.dormancy_threshold_daylength = threshold_daylength
    field.crops = [crop]
    rainfall = 10.3

    with patch("RUFAS.routines.field.crop.dormancy.Dormancy.enter_dormancy", new_callable=MagicMock) as dormancy, \
            patch("RUFAS.routines.field.crop.biomass_allocation.BiomassAllocation.partition_biomass",
                  new_callable=MagicMock) as biomass, \
            patch("RUFAS.routines.field.soil.carbon_cycling.residue_partition.ResiduePartition.add_residue_to_pools") \
            as add_residue:
        field._assess_dormancy(daylength, rainfall)

    if daylength <= threshold_daylength:
        assert dormancy.call_count == 1
        assert biomass.call_count == 1
        assert add_residue.call_count == 1
    else:
        dormancy.assert_not_called()
        biomass.assert_not_called()


@pytest.mark.parametrize("species,specs", [
    ("corn_grain", {}),  # no additional arguments
    ("alfalfa_hay", {"minimum_temperature": -2.1, "id": 123})  # supported species, with alteration
])
def test_make_supported_crop(species: str, specs: dict):
    """ensure that supported crops are properly created."""
    # check that attributes are correct
    crop = Field._make_supported_crop(species, **specs)
    assert crop.data.species == species
    for key, val in specs.items():
        assert getattr(crop.data, key) == val

    if len(specs) > 0:
        assert "altered" in crop.data.name
    else:
        assert "altered" not in crop.data.name

    # failing cases
    with pytest.raises(Exception):
        Field._make_supported_crop("fake_crop")
    with pytest.raises(Exception):
        Field._make_supported_crop("corn", bad_attr=17.35)


@pytest.mark.parametrize("config", [
    {"species": "grass"},  # custom species, with generic defaults
    {"species": "cottonwood", "is_perennial": True},  # custom species and attribute
    {"minimum_temperature": -10},  # no species name
])
def test_make_custom_crop(config: dict):
    """checks that custom crop attributes are set correctly"""
    crop = Field._make_custom_crop(**config)
    for key, val in config.items():
        assert getattr(crop.data, key) == val


@pytest.mark.parametrize("config", [
    {"species": "corn"},  # supported species
    {"species": "corn", "minimum_temperature": -2.0, "is_perennial": True},  # supported species, with alterations
    {"species": "grass"},  # unsupported species, generic attributes
    {"species": "cottonwood", "is_perennial": True},  # custom species and attributes
    {"minimum_temperature": -2.0},  # generic custom crop, with alterations
])
def test_make_crop_from_config_dict(config: dict):
    supported_crops = set(item.value for item in CropSpecies)
    has_supported_species = "species" in config.keys() and str(config["species"]) in supported_crops
    Field._make_supported_crop = MagicMock()
    Field._make_custom_crop = MagicMock()

    Field._make_crop_from_config_dict(config)

    if has_supported_species:
        Field._make_supported_crop.assert_called_once()
        Field._make_custom_crop.assert_not_called()
    else:
        Field._make_supported_crop.assert_not_called()
        Field._make_custom_crop.assert_called_once()


@pytest.mark.parametrize("mix_name,requested_n,requested_p,depth,remainder,year,day,field_size,fertilizer_applied", {
    ("test_mix_1", 80.0, 30.0, 0.0, 1.0, 1993, 100, 3.1, True),
    ("test_mix_2", 150.0, 89.0, 25.0, 0.89, 2001, 240, 1.3, True),
    ("test_mix_3", 10.0, 90.33, 100.0, 0.5, 1992, 30, 2.44, True),
    ("test_mix_4", 0.0, 50.0, 0.0, 1.0, 1996, 60, 1.45, True),
    ("test_mix_5", 67.5, 0.0, 0.0, 1.0, 1998, 200, 2.3, True),
    ("test_mix_6", 0.0, 0.0, 0.0, 1.0, 1988, 120, 0.5, False),
})
def test_execute_fertilizer_application(mix_name: str, requested_n: float, requested_p: float, depth: float,
                                        remainder: float, year: int, day: int, field_size: float,
                                        fertilizer_applied: bool) -> None:
    """Tests that fertilizer applications are being correctly executed and recorded."""
    field_data = FieldData(name="test", field_size=field_size)
    field = Field(field_data=field_data, fertilizer_mixes={mix_name: {"N": 0.3, "P": 0.2, "K": 0.5}},
                  manure_manager=MagicMock(ManureManager))
    field._formulate_fertilizer_required = MagicMock(return_value={"total_mass": 100, "nitrogen_mass": 20,
                                                                   "phosphorus_mass": 15,
                                                                   "potassium_mass": 10})
    field.fertilizer_applicator.apply_fertilizer = MagicMock()
    field._record_fertilizer_application = MagicMock()

    with patch.object(om, "_get_timestamp") as mocked_timestamp:
        mocked_timestamp.return_value = "00-Jan-1970_Thu_00-00-00"

        field._execute_fertilizer_application(mix_name, requested_n, requested_p, depth, remainder, year, day)

        if fertilizer_applied:
            expected_nitrogen_fraction = 0.2
            field._formulate_fertilizer_required.assert_called_once_with(0.3, 0.2, 0.5, requested_n, requested_p)
            field.fertilizer_applicator.apply_fertilizer.assert_called_once_with(15, 100, expected_nitrogen_fraction,
                                                                                 0.0, 0.0, depth, remainder, field_size)
            field._record_fertilizer_application.assert_called_once_with(mix_name, 100, 20, 15, 10, depth, remainder,
                                                                         year, day)
        else:
            expected_info_map = {"prefix": "field='test'", "date": {"year": year, "day": day},
                                 "timestamp": "00-Jan-1970_Thu_00-00-00"}
            expected_log_message = "Tried to apply fertilizer with no nitrogen or phosphorus requested."
            actual = om.logs_pool["field='test'.fertilizer_application_log"]
            assert actual["info_maps"].__contains__(expected_info_map)
            assert actual["values"].__contains__(expected_log_message)
            field._formulate_fertilizer_required.assert_not_called()
            field.fertilizer_applicator.apply_fertilizer.assert_not_called()
            field._record_fertilizer_application.assert_not_called()


@pytest.mark.parametrize("field_name,mix_name,available_mixes,expected_message", [
    ("test_field_1", "halo_alien_mix", {}, "\"'test_field_1': expected to have fertilizer mix for 'halo_alien_mix', "
                                           "received '{'100_0_0': {'N': 1.0, 'P': 0.0, 'K': 0.0}, '26_4_24': "
                                           "{'N': 0.26, 'P': 0.04, 'K': 0.24}}'.\""),
    ("test_field_2", "101_0_0", {"50_22_12": {"N": 0.5, "P": 0.22, "K": 0.12}},
     "\"'test_field_2': expected to have fertilizer mix for '101_0_0', received '{'50_22_12': {'N': 0.5, 'P': 0.22, "
     "'K': 0.12}, '100_0_0': {'N': 1.0, 'P': 0.0, 'K': 0.0}, '26_4_24': {'N': 0.26, 'P': 0.04, 'K': 0.24}}'.\"")
])
def test_execute_fertilizer_application_error(field_name: str, mix_name: str, available_mixes: Dict,
                                              expected_message: str) -> None:
    """Tests that errors are correctly raised when a mix is specified to be used but is not listed in the available
        mixes."""
    field = Field(field_data=FieldData(name=field_name), fertilizer_mixes=available_mixes,
                  manure_manager=MagicMock(ManureManager))
    with pytest.raises(KeyError) as e:
        field._execute_fertilizer_application(mix_name, 10.0, 10.0, 0.0, 1.0, 1994, 120)
    assert str(e.value) == expected_message


@pytest.mark.parametrize("depth,remainder,expected_depth,expected_remainder,invalid_combination", [
    (1000.0, 0.1, 950.0, 0.1, False),
    (100.0, 1.0, 0.0, 1.0, True),
    (0.0, 0.9, 0.0, 1.0, True)
])
def test_execute_fertilizer_application_with_invalid_args(depth: float, remainder: float, expected_depth: float,
                                                          expected_remainder: float, invalid_combination: bool) -> None:
    """Tests that fertilizer applications with invalid arguments are caught, recorded in the OutputManager and execution
        with corrected values takes place."""
    field = Field(field_data=FieldData(name="test", field_size=1.2), manure_manager=MagicMock(ManureManager))
    field.soil.data.soil_layers[-1].bottom_depth = 950.0
    with patch("RUFAS.routines.field.field.field.Field._record_nutrient_application_error",
               new_callable=MagicMock) as patched_error, \
            patch("RUFAS.routines.field.field.field.Field._formulate_fertilizer_required", new_callable=MagicMock,
                  return_value={"total_mass": 100.0, "phosphorus_mass": 50.0, "nitrogen_mass": 50.0,
                                "potassium_mass": 0.0}) as patched_formulator, \
            patch("RUFAS.routines.field.field.fertilizer_application.FertilizerApplication.apply_fertilizer",
                  new_callable=MagicMock) as patched_applicator, \
            patch("RUFAS.routines.field.field.field.Field._record_fertilizer_application",
                  new_callable=MagicMock) as patched_recorder:
        field._execute_fertilizer_application("26_4_24", 50.0, 50.0, depth, remainder, 1994, 200)

        if invalid_combination:
            patched_error.assert_called_once_with(depth, remainder, "fertilizer_application_error", 1994, 200)
        else:
            patched_error.assert_called_once_with(depth, None, "fertilizer_application_error", 1994, 200)
        patched_formulator.assert_called_once_with(0.26, 0.04, 0.24, 50.0, 50.0)
        patched_applicator.assert_called_once_with(50.0, 100.0, 0.5, 0.0, 0.0, expected_depth, expected_remainder, 1.2)
        patched_recorder.assert_called_once_with("26_4_24", 100.0, 50.0, 50.0, 0.0, expected_depth, expected_remainder,
                                                 1994, 200)


@pytest.mark.parametrize("nitrogen,phosphorus,mixes,expected", [
    (100, 20, {"100_0_0": {"N": 1.0, "P": 0.0, "K": 0.0}, "26_4_24": {"N": 0.26, "P": 0.04, "K": 0.24}}, "26_4_24"),
    (50, 60, {"30_40_50": {"N": 0.3, "P": 0.4, "K": 0.5}}, "30_40_50"),
    (22.5, 33, {"25_15_28": {"N": 0.25, "P": 0.15, "K": 0.28}, "33_40_3": {"N": 0.33, "P": 0.4, "K": 0.28},
                "40_22_6": {"N": 0.4, "P": 0.22, "K": 0.06}}, "33_40_3"),
    (245.0, 43.0, {"0_0_60": {"N": 0.0, "P": 0.0, "K": 0.6}, "26_4_24": {"N": 0.26, "P": 0.04, "K": 0.24}}, "26_4_24")
])
def test_determine_optimal_fertilizer_mix(nitrogen: float, phosphorus: float, mixes: Dict[str, Dict[str, float]],
                                          expected: float) -> None:
    """Tests that the optimal mix for meeting the requested nutrients is found correctly."""
    actual = Field._determine_optimal_fertilizer_mix(nitrogen, phosphorus, mixes)
    assert actual == expected


@pytest.mark.parametrize("nitrogen_frac,phosphorus_frac,potassium_frac,requested_nitrogen,requested_phosphorus,"
                         "expected", [
                             (0.2, 0.1, 0.3, 100.0, 80.0, {"total_mass": 800.0, "nitrogen_mass": 160.0,
                                                           "phosphorus_mass": 80.0, "potassium_mass": 240.0}),
                             (0.82, 0.0, 0.0, 200.0, 50.0, {"total_mass": 243.90243902439025, "nitrogen_mass": 200.0,
                                                            "phosphorus_mass": 0.0, "potassium_mass": 0.0}),
                             (0.4, 0.2, 0.1, 80.0, 40.0, {"total_mass": 200.0, "nitrogen_mass": 80.0,
                                                          "phosphorus_mass": 40.0, "potassium_mass": 20.0}),
                             (0.05, 0.1, 0.3, 45.0, 100.0, {"total_mass": 1000.0, "nitrogen_mass": 50.0,
                                                            "phosphorus_mass": 100.0, "potassium_mass": 300.0})
                         ])
def test_formulate_fertilizer_required(nitrogen_frac: float, phosphorus_frac: float, potassium_frac: float,
                                       requested_nitrogen: float, requested_phosphorus: float,
                                       expected: Dict[str, float]) -> None:
    """Tests that fertilizer formulations are made correctly."""
    actual = Field._formulate_fertilizer_required(nitrogen_frac, phosphorus_frac, potassium_frac, requested_nitrogen,
                                                  requested_phosphorus)
    assert actual == expected


@pytest.mark.parametrize("mix_name,total_mass,nitrogen_mass,phosphorus_mass,potassium_mass,depth,remainder,year,day,"
                         "field_name,field_size", [
                             ("mix_1", 100, 20, 20, 20, 35.0, 0.8, 1992, 90, "field_1", 1.4),
                             ("mix_2", 30, 10, 3, 3, 0.0, 1.0, 1994, 120, "field_2", 4.3)
                         ])
def test_record_fertilizer_application(mix_name: str, total_mass: float, nitrogen_mass: float, phosphorus_mass: float,
                                       potassium_mass: float, depth: float, remainder: float, year: int, day: int,
                                       field_name: str, field_size: float) -> None:
    """Tests that fertilizer applications are correctly recorded in the OutputManager."""
    field = Field(field_data=FieldData(name=field_name, field_size=field_size),
                  manure_manager=MagicMock(ManureManager))

    field._record_fertilizer_application(mix_name, total_mass, nitrogen_mass, phosphorus_mass, potassium_mass, depth,
                                         remainder, year, day)

    expected_info_map = {"prefix": f"field='{field_name}'", "date": {"year": year, "day": day},
                         "mix_name": mix_name, "field_size": field_size}
    expected_value = {"mass": total_mass, "nitrogen": nitrogen_mass, "phosphorus": phosphorus_mass,
                      "potassium": potassium_mass, "application_depth": depth, "surface_remainder_fraction": remainder}
    actual = om.variables_pool[f"field='{field_name}'.fertilizer_application"]
    assert actual["info_maps"].__contains__(expected_info_map)
    assert actual["values"].__contains__(expected_value)


@pytest.mark.parametrize("nitrogen,phosphorus,coverage,depth,remainder,year,day,supplement,fertilizer_applied,"
                         "only_nitrogen_unmet,supplied_manure,expected_request,expected_unmet_nitrogen,"
                         "expected_unmet_phosphorus", [
                             (75.0, 75.0, 0.9, 0.0, 1.0, 1993, 175, True, True, False,
                              NutrientRequestResults(nitrogen=50.0, phosphorus=50.0, dry_matter=250.0,
                                                     dry_matter_fraction=0.33, organic_nitrogen_fraction=0.3,
                                                     inorganic_nitrogen_fraction=0.7, ammonium_nitrogen_fraction=0.25,
                                                     organic_phosphorus_fraction=0.5,
                                                     inorganic_phosphorus_fraction=0.5),
                              NutrientRequest(nitrogen=75.0, phosphorus=75.0), 25.0, 25.0),
                             (100.0, 0.0, 0.88, 120.0, 0.7, 2003, 200, True, True, True,
                              NutrientRequestResults(nitrogen=50.0, phosphorus=50.0, dry_matter=250.0,
                                                     dry_matter_fraction=0.33, organic_nitrogen_fraction=0.3,
                                                     inorganic_nitrogen_fraction=0.7, ammonium_nitrogen_fraction=0.25,
                                                     organic_phosphorus_fraction=0.4,
                                                     inorganic_phosphorus_fraction=0.6),
                              NutrientRequest(nitrogen=100.0, phosphorus=0.0), 50.0, 0.0),
                             (50.0, 50.0, 0.91, 200.0, 0.45, 1998, 155, True, False, False,
                              NutrientRequestResults(nitrogen=50.0, phosphorus=50.0, dry_matter=250.0,
                                                     dry_matter_fraction=0.33, organic_nitrogen_fraction=0.3,
                                                     inorganic_nitrogen_fraction=0.7, ammonium_nitrogen_fraction=0.25,
                                                     organic_phosphorus_fraction=0.544,
                                                     inorganic_phosphorus_fraction=0.456),
                              NutrientRequest(nitrogen=50.0, phosphorus=50.0), 0.0, 0.0),
                             (65.0, 40.0, 0.77, 75.0, 0.78, 1999, 160, True, True, False, None,
                              NutrientRequest(nitrogen=65.0, phosphorus=40.0), 65.0, 40.0),
                             (0, 0, 0.5, 0.0, 1.0, 1996, 155, True, False, False, None, None, 0.0, 0.0),
                             (75.0, 50.0, 0.7, 0.0, 1.0, 2010, 120, False, True, True,
                              NutrientRequestResults(nitrogen=50.0, phosphorus=50.0, dry_matter=250.0,
                                                     dry_matter_fraction=0.33, organic_nitrogen_fraction=0.3,
                                                     inorganic_nitrogen_fraction=0.7, ammonium_nitrogen_fraction=0.25,
                                                     organic_phosphorus_fraction=0.544,
                                                     inorganic_phosphorus_fraction=0.456),
                              NutrientRequest(nitrogen=75.0, phosphorus=50.0), 25.0, 0.0),
                             (50.0, 50.0, 0.7, 0.0, 1.0, 2010, 120, False, False, False,
                              NutrientRequestResults(nitrogen=50.0, phosphorus=50.0, dry_matter=250.0,
                                                     dry_matter_fraction=0.33, organic_nitrogen_fraction=0.3,
                                                     inorganic_nitrogen_fraction=0.7, ammonium_nitrogen_fraction=0.25,
                                                     organic_phosphorus_fraction=0.544,
                                                     inorganic_phosphorus_fraction=0.456),
                              NutrientRequest(nitrogen=50.0, phosphorus=50.0), 50.0, 0.0),
                         ])
def test_execute_manure_application(nitrogen: float, phosphorus: float, coverage: float, depth: float, remainder: float,
                                    year: int, day: int, supplement: bool, fertilizer_applied: bool,
                                    only_nitrogen_unmet: bool, supplied_manure: NutrientRequestResults,
                                    expected_request: NutrientRequest, expected_unmet_nitrogen: float,
                                    expected_unmet_phosphorus: float) -> None:
    """Tests that manure is applied to the soil correctly."""
    mocked_manure_manager = MagicMock(ManureManager)
    mocked_manure_manager.request_nutrients = MagicMock(return_value=supplied_manure)
    field = Field(field_data=FieldData(name="test", field_size=1.4, supplement_manure_nutrient_deficiencies=supplement),
                  manure_manager=mocked_manure_manager)
    field.manure_applicator.apply_machine_manure = MagicMock()
    field._record_manure_application = MagicMock()
    field._determine_optimal_fertilizer_mix = MagicMock(return_value="expected_optimal_mix")
    field._execute_fertilizer_application = MagicMock()

    with patch.object(om, "add_log") as log, \
            patch.object(om, "add_warning") as warn:
        field._execute_manure_application(nitrogen, phosphorus, coverage, depth, remainder, year, day)

        if nitrogen == phosphorus == 0.0:
            log.assert_called_once()

            mocked_manure_manager.request_nutrients.assert_not_called()
            field.manure_applicator.apply_machine_manure.assert_not_called()
            field._record_manure_application.assert_not_called()
            warn.assert_not_called()
            field._determine_optimal_fertilizer_mix.assert_not_called()
            field._execute_fertilizer_application.assert_not_called()
        else:
            log.assert_not_called()
            expected_total_inorganic_fraction = 0.14  # equal to (50.0 / 250.0) * 0.7
            expected_total_organic_fraction = 0.06  # equal to (50.0 / 250.0) * 0.3

            if supplied_manure is not None:
                mocked_manure_manager.request_nutrients.assert_called_once_with(expected_request)
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
                    water_extractable_inorganic_phosphorus_fraction=supplied_manure.inorganic_phosphorus_fraction)
                field._record_manure_application.assert_called_once_with(
                    dry_matter_mass=supplied_manure.dry_matter,
                    dry_matter_fraction=supplied_manure.dry_matter_fraction,
                    field_coverage=coverage,
                    nitrogen=supplied_manure.nitrogen,
                    phosphorus=supplied_manure.phosphorus,
                    potassium=None,
                    application_depth=depth,
                    surface_remainder_fraction=remainder,
                    year=year,
                    day=day)

            if fertilizer_applied and not supplement:
                warn.assert_called_once()
                field._determine_optimal_fertilizer_mix.assert_not_called()
                field._execute_fertilizer_application.assert_not_called()
            elif not fertilizer_applied and not supplement:
                warn.assert_not_called()
                field._determine_optimal_fertilizer_mix.assert_not_called()
                field._execute_fertilizer_application.assert_not_called()
            elif fertilizer_applied and only_nitrogen_unmet and supplement:
                warn.assert_not_called()
                field._determine_optimal_fertilizer_mix.assert_not_called()
                field._execute_fertilizer_application.assert_called_once_with("100_0_0", expected_unmet_nitrogen,
                                                                              expected_unmet_phosphorus, depth,
                                                                              remainder, year, day)
            elif fertilizer_applied and not only_nitrogen_unmet and supplement:
                warn.assert_not_called()
                field._determine_optimal_fertilizer_mix.assert_called_once_with(expected_unmet_nitrogen,
                                                                                expected_unmet_phosphorus,
                                                                                field.available_fertilizer_mixes)
                field._execute_fertilizer_application.assert_called_once_with("expected_optimal_mix",
                                                                              expected_unmet_nitrogen,
                                                                              expected_unmet_phosphorus, depth,
                                                                              remainder, year, day)


@pytest.mark.parametrize("depth,remainder,expected_depth,expected_remainder,invalid_combination", [
    (100.0, 1.0, 0.0, 1.0, True),
    (0.0, 0.76, 0.0, 1.0, True),
    (1000.0, 0.2, 950.0, 0.2, False)
])
def test_execute_manure_application_with_invalid_args(depth: float, remainder: float, expected_depth: float,
                                                      expected_remainder: float, invalid_combination: bool) -> None:
    """Tests that the manure application executor raises errors and runs correctly when invalid arguments are passed."""
    mocked_manure_manager = MagicMock(ManureManager)
    supplied_nutrients = NutrientRequestResults(
        nitrogen=50.0,
        phosphorus=50.0,
        total_manure_mass=150.0,
        dry_matter=100.0,
        dry_matter_fraction=0.66
    )
    mocked_manure_manager.request_nutrients = MagicMock(return_value=supplied_nutrients)
    field = Field(field_data=FieldData(name="test", field_size=1.89), manure_manager=mocked_manure_manager)
    field.soil.data.soil_layers[-1].bottom_depth = 950.0
    expected_total_inorganic_fraction = 0.15  # equal to (50.0 / 100.0) * 0.3
    expected_total_organic_fraction = 0.35  # equal to (50.0 / 100.0) * 0.7

    with patch("RUFAS.routines.field.field.field.Field._record_nutrient_application_error",
               new_callable=MagicMock) as patched_error, \
            patch("RUFAS.routines.field.field.manure_application.ManureApplication.apply_machine_manure",
                  new_callable=MagicMock) as patched_manure_applicator, \
            patch("RUFAS.routines.field.field.field.Field._record_manure_application",
                  new_callable=MagicMock) as patched_recorder, \
            patch("RUFAS.routines.field.field.field.Field._determine_optimal_fertilizer_mix",
                  new_callable=MagicMock, return_value="26_4_24") as patched_optimizer, \
            patch("RUFAS.routines.field.field.field.Field._execute_fertilizer_application",
                  new_callable=MagicMock) as patched_fertilizer_applicator:
        field._execute_manure_application(50.0, 50.0, 0.8, depth, remainder, 2000, 133)

        if invalid_combination:
            patched_error.assert_called_once_with(depth, remainder, "manure_application_error", 2000, 133)
        else:
            patched_error.assert_called_once_with(depth, None, "manure_application_error", 2000, 133)
        mocked_manure_manager.request_nutrients.assert_called_once_with(NutrientRequest(nitrogen=50.0, phosphorus=50.0))
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
            water_extractable_inorganic_phosphorus_fraction=0.5)
        patched_recorder.assert_called_once_with(dry_matter_mass=100.0,
                                                 dry_matter_fraction=0.66,
                                                 field_coverage=0.8,
                                                 nitrogen=50.0,
                                                 phosphorus=50.0,
                                                 potassium=None,
                                                 application_depth=expected_depth,
                                                 surface_remainder_fraction=expected_remainder,
                                                 year=2000,
                                                 day=133)
        patched_optimizer.assert_not_called()
        patched_fertilizer_applicator.assert_not_called()


@pytest.mark.parametrize("field_name,field_size,dry_mass,dry_fraction,coverage,nitrogen,phosphorus,depth,remainder,"
                         "year,day,expected_info,expected_values,potassium", [
                             ("test_1", 1.3, 100, 0.1, 0.8, 10, 15, 0.0, 1.0, 1991, 75,
                              {"prefix": "field='test_1'", "date": {"year": 1991, "day": 75}, "field_size": 1.3},
                              {"dry_matter_mass": 100, "dry_matter_fraction": 0.1, "application_depth": 0.0,
                               "surface_remainder_fraction": 1.0, "field_coverage": 0.8, "nitrogen": 10,
                               "phosphorus": 15, "potassium": 12.5}, 12.5),
                             ("test_2", 2.4, 144.6, 0.3, 0.92, 40, 43.1, 45.0, 0.85, 1994, 200,
                              {"prefix": "field='test_2'", "date": {"year": 1994, "day": 200}, "field_size": 2.4},
                              {"dry_matter_mass": 144.6, "dry_matter_fraction": 0.3, "application_depth": 45.0,
                               "surface_remainder_fraction": 0.85, "field_coverage": 0.92, "nitrogen": 40,
                               "phosphorus": 43.1, "potassium": 14.55}, 14.55),
                             ("test_3", 0.66, 266.5, 0.44, 0.95, 100.5, 78.0, 120.0, 0.7, 2009, 150,
                              {"prefix": "field='test_3'", "date": {"year": 2009, "day": 150}, "field_size": 0.66},
                              {"dry_matter_mass": 266.5, "dry_matter_fraction": 0.44, "application_depth": 120.0,
                               "surface_remainder_fraction": 0.7, "field_coverage": 0.95,
                               "nitrogen": 100.5, "phosphorus": 78.0, "potassium": None}, None)
                         ])
def test_record_manure_application(field_name: str, field_size: float, dry_mass: float, dry_fraction: float,
                                   coverage: float, nitrogen: float, phosphorus: float, depth: float, remainder: float,
                                   year: int, day: int, expected_info: Dict, expected_values: Dict,
                                   potassium: float) -> None:
    """Tests that manure applications are recorded correctly."""
    field = Field(field_data=FieldData(name=field_name, field_size=field_size), manure_manager=MagicMock(ManureManager))

    field._record_manure_application(dry_mass, dry_fraction, coverage, nitrogen, phosphorus, depth, remainder, year,
                                     day, potassium)

    actual = om.variables_pool[f"field='{field_name}'.manure_application"]
    assert actual["info_maps"].__contains__(expected_info)
    assert actual["values"].__contains__(expected_values)


@pytest.mark.parametrize("depth,remainder,name,year,day,expected_info_map,expected_error_message", [
    (100.0, 1.0, "manure_application_error", 1998, 200,
     {"prefix": "field='test'", "date": {"year": 1998, "day": 200}, "timestamp": "00-Jan-1970_Thu_00-00-00"},
     "Invalid application depth (100.0) and surface remainder fraction (1.0). Defaulting to application depth of 0.0 "
     "mm and a surface remainder fraction of 1.0."),
    (800.0, None, "fertilizer_application_error", 2005, 100,
     {"prefix": "field='test'", "date": {"year": 2005, "day": 100}, "timestamp": "00-Jan-1970_Thu_00-00-00"},
     "Invalid application depth (800.0) is lower than the bottom depth of the soil profile, setting the application "
     "depth to be at the bottom of the soil profile.")
])
def test_record_nutrient_application_error(depth: float, remainder: float, name: str, year: int, day: int,
                                           expected_info_map: dict, expected_error_message: str) -> None:
    """Tests that manure and fertilizer application errors are correctly recorded to the OutputManager."""
    with patch.object(om, "_get_timestamp") as mocked_timestamp:
        field = Field(field_data=FieldData(name="test"), manure_manager=MagicMock(ManureManager))
        mocked_timestamp.return_value = "00-Jan-1970_Thu_00-00-00"

        field._record_nutrient_application_error(depth, remainder, name, year, day)

        expected_error_name = expected_info_map["prefix"] + "." + name
        actual = om.errors_pool[expected_error_name]
        assert actual["info_maps"].__contains__(expected_info_map)
        assert actual["values"].__contains__(expected_error_message)


@pytest.mark.parametrize("field_size,crops_growing,residue,light,mean_temp,min_temp,max_temp,annual_mean_temp,"
                         "transpiration", [
                             (1.5, False, 34.5, 128, 22.5, 18.9, 25.6, 19.22, 5.2),
                             (2.4, True, 40.9, 150, 28, 24.55, 31.2, 17.9, 3.44),
                             (0.8, True, 12.22, 222, 18.7, 13.44, 23.44, 16.4, 1.33)
                         ])
def test_execute_daily_processes(field_size: float, crops_growing: bool, residue: float, light: float, mean_temp: float,
                                 min_temp: float, max_temp: float, annual_mean_temp: float,
                                 transpiration: float) -> None:
    """Tests that all component processes and subroutines are correctly called in Field."""
    with patch.multiple("RUFAS.routines.field.crop.crop_data.CropData",
                        is_mature=PropertyMock(return_value=not crops_growing),
                        is_dormant=PropertyMock(return_value=not crops_growing)):
        field_data = FieldData(field_size=field_size, current_residue=residue)
        incorp = Field(field_data=field_data, manure_manager=MagicMock(ManureManager))
        crop_1 = Crop()
        crop_1.data.max_transpiration = transpiration
        crop_2 = Crop()
        crop_2.data.max_transpiration = transpiration
        incorp.crops = [crop_1, crop_2]
        current_conditions = CurrentDayConditions(incoming_light=light, mean_air_temperature=mean_temp,
                                                  min_air_temperature=min_temp, max_air_temperature=max_temp,
                                                  annual_mean_air_temperature=annual_mean_temp)

        incorp.soil.snow.update_snow = MagicMock()
        incorp._determine_total_above_ground_biomass = MagicMock(return_value=89)
        incorp.soil.soil_temp.daily_soil_temperature_update = MagicMock()
        incorp._cycle_water = MagicMock()
        for crop in incorp.crops:
            crop.heat_units.absorb_heat_units = MagicMock()
            crop.root_development = MagicMock()
            crop.nitrogen_incorporation.incorporate_nitrogen = MagicMock()
            crop.phosphorus_incorporation.incorporate_phosphorus = MagicMock()
            crop.growth_constraints.constrain_growth = MagicMock()
            crop.leaf_area_index.grow_canopy = MagicMock()
            crop.biomass_allocation.allocate_biomass = MagicMock()
        mocked_time = MagicMock(Time)
        setattr(mocked_time, "year", 2023)
        setattr(mocked_time, "day", 178)
        incorp._execute_daily_processes(current_conditions, mocked_time)

        incorp.soil.snow.update_snow.assert_called_once_with(current_day_conditions=current_conditions,
                                                             day=mocked_time.day)
        incorp._determine_total_above_ground_biomass.assert_called_once()
        incorp.soil.soil_temp.daily_soil_temperature_update.assert_called_once_with(light, mean_temp, min_temp,
                                                                                    max_temp, 89 + residue, 0,
                                                                                    annual_mean_temp)
        incorp._cycle_water.assert_called_once_with(current_conditions, mocked_time)
        for crop in incorp.crops:
            if crops_growing:
                crop.heat_units.absorb_heat_units.assert_called_once_with(mean_temp, min_temp, max_temp)
                crop.root_development.develop_roots.assert_called_once()
                crop.nitrogen_incorporation.incorporate_nitrogen.assert_called_once_with(incorp.soil.data)
                crop.phosphorus_incorporation.incorporate_phosphorus.assert_called_once_with(incorp.soil.data)
                crop.growth_constraints.constrain_growth.assert_called_once_with(transpiration, mean_temp)
                crop.leaf_area_index.grow_canopy.assert_called_once()
                crop.biomass_allocation.allocate_biomass.assert_called_once_with(light)
            else:
                crop.heat_units.absorb_heat_units.assert_not_called()
                crop.root_development.develop_roots.assert_not_called()
                crop.nitrogen_incorporation.incorporate_nitrogen.assert_not_called()
                crop.phosphorus_incorporation.incorporate_phosphorus.assert_not_called()
                crop.growth_constraints.constrain_growth.assert_not_called()
                crop.leaf_area_index.grow_canopy.assert_not_called()
                crop.biomass_allocation.allocate_biomass.assert_not_called()


@pytest.mark.parametrize("field_size,rainfall,runoff,high_water_table,residue,light,min_temp,max_temp,mean_temp,"
                         "surface_residue,crop_1_proportion,crop_2_proportion,crops_growing", [
                             (1.9, 4.66, 1.22, False, 30.6, 200, 16.5, 20.5, 18.5, 44.5, 0.6, 0.4, True),
                             (2.3, 5.6, 2.1, True, 44.5, 250, 22.33, 25.36, 24.6, 80.4, 0.77, 0.23, False),
                             (2.3, 5.6, 2.1, True, 44.5, 250, 22.33, 25.36, 24.6, 80.4, 0.0, 0.0, False)
                         ])
def test_cycle_water(field_size: float, rainfall: float, runoff: float, high_water_table: bool, residue: float,
                     light: float, min_temp: float, max_temp: float, mean_temp: float, surface_residue: float,
                     crop_1_proportion: float, crop_2_proportion: float, crops_growing: bool) -> None:
    """Tests that cycle_water() correctly executes all water processes on its soil profile and the crops it contains."""
    with patch("RUFAS.routines.field.crop.crop_data.CropData.in_growing_season", new_callable=PropertyMock,
               return_value=crops_growing):
        soil_data = SoilData(field_size=field_size, accumulated_runoff=runoff, water_evaporated=3.5,
                             water_sublimated=1.0)
        soil_data.plant_surface_residue = surface_residue
        soil = Soil(soil_data)
        crop_data_1 = CropData(field_proportion=crop_1_proportion, max_transpiration=44.1, cumulative_evaporation=105.5,
                               cumulative_transpiration=205.1, cumulative_potential_evapotranspiration=400.19,
                               water_uptake=3.5)
        crop_1 = Crop(crop_data_1)
        crop_data_2 = CropData(field_proportion=crop_2_proportion, max_transpiration=39.5, cumulative_evaporation=112.4,
                               cumulative_transpiration=219.2, cumulative_potential_evapotranspiration=480.1,
                               water_uptake=3.25)
        crop_2 = Crop(crop_data_2)
        current_conditions = CurrentDayConditions(incoming_light=light, min_air_temperature=min_temp,
                                                  precipitation=rainfall, max_air_temperature=max_temp,
                                                  mean_air_temperature=mean_temp)
        field_data = FieldData(field_size=field_size, current_residue=residue,
                               seasonal_high_water_table=high_water_table)
        incorp = Field(field_data=field_data, soil=soil, manure_manager=MagicMock(ManureManager))
        incorp.crops = [crop_1, crop_2]

        incorp.soil.infiltration.infiltrate = MagicMock()
        incorp.soil.percolation.percolate = MagicMock()
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

        crop_1.water_dynamics.set_maximum_transpiration = MagicMock()
        crop_1.water_dynamics.cycle_water = MagicMock()
        crop_1.water_uptake.uptake_water = MagicMock()
        crop_2.water_dynamics.set_maximum_transpiration = MagicMock()
        crop_2.water_dynamics.cycle_water = MagicMock()
        crop_2.water_uptake.uptake_water = MagicMock()
        mocked_time = MagicMock(Time)
        setattr(mocked_time, "year", 2023)
        setattr(mocked_time, "day", 178)

        incorp._cycle_water(current_conditions, mocked_time)

        incorp._determine_watering_amount.assert_called_once_with(rainfall=rainfall, year=mocked_time.year,
                                                                  day=mocked_time.day, irrigation=0.0)
        incorp._handle_water_in_crop_canopies.assert_called_once_with(rainfall)
        incorp._determine_potential_evapotranspiration.assert_called_once_with(light, max_temp, min_temp,
                                                                               mean_temp)
        incorp._evaporate_from_crop_canopies.assert_called_once_with(33.5)
        incorp.soil.infiltration.infiltrate.assert_called_once_with(2.0)
        incorp.soil.percolation.percolate.assert_called_once_with(high_water_table)
        incorp.soil.soil_erosion.erode.assert_called_once_with(field_size, 0.02, residue, rainfall)
        incorp.soil.phosphorus_cycling.cycle_phosphorus.assert_called_once_with(2.0, runoff, field_size, mean_temp)
        incorp.soil.nitrogen_cycling.cycle_nitrogen.assert_called_once_with(field_size)
        incorp.soil.carbon_cycling.cycle_carbon.assert_called_once_with(2.0, mean_temp, field_size)
        expected_remaining_demand = 30.5
        crop_1.water_dynamics.set_maximum_transpiration.assert_called_once_with(expected_remaining_demand)
        crop_2.water_dynamics.set_maximum_transpiration.assert_called_once_with(expected_remaining_demand)
        expected_average_transpiration = 44.1 * crop_1_proportion + 39.5 * crop_2_proportion
        incorp._determine_soil_evaporation_and_sublimation_adjusted.assert_called_once_with(
            40.0, surface_residue, 0, expected_remaining_demand, expected_average_transpiration)
        incorp.soil.snow.sublimate.assert_called_once_with(10.5)
        expected_soil_evaporation_after_sublimation = 10.5 - 1.0
        incorp.soil.evaporation.evaporate.assert_called_once_with(expected_soil_evaporation_after_sublimation)
        expected_actual_evaporation = 33.5 - (expected_remaining_demand - 4.5)
        if crops_growing:
            crop_1.water_uptake.uptake_water.assert_called_once_with(incorp.soil.data)
            crop_1.water_dynamics.cycle_water.assert_called_once_with(expected_actual_evaporation, 3.5, 33.5)
            crop_2.water_uptake.uptake_water.assert_called_once_with(incorp.soil.data)
            crop_2.water_dynamics.cycle_water.assert_called_once_with(expected_actual_evaporation, 3.25, 33.5)
        else:
            assert crop_1.data.cumulative_evaporation == 0
            assert crop_1.data.cumulative_transpiration == 0
            assert crop_1.data.cumulative_potential_evapotranspiration == 0
            assert crop_2.data.cumulative_evaporation == 0
            assert crop_2.data.cumulative_transpiration == 0
            assert crop_2.data.cumulative_potential_evapotranspiration == 0


@pytest.mark.parametrize("rainfall,days_into_interval,water_deficit,watering_occurs,irrigation,old_method",
                         [
                             (3.4, 3, 1.5, False, 0, False),  # No watering because water_occurs is False
                             (3.1, 5, 2.3, True, 0, False),
                             # No watering because rainfall takes care of watering
                             (0.2, 5, 3.6, True, 0, False),
                             # Watering occurs because water deficit has not been met
                             (0.19, 4, 2.8, True, 0, False),
                             # No watering occurs because interval has not been met
                             (0.2, 5, 3.6, True, 9.24, False),
                             (0.2, 5, 3.6, False, 77.7, True)
                         ])
def test_determine_watering_amount(rainfall: float, days_into_interval: int, water_deficit: float,
                                   watering_occurs: float, irrigation: float, old_method: bool) -> None:
    """Tests that the correct amount of water to be used to water is field is calculated, and that the counters and
        totals are updated correctly."""
    mocked_time = MagicMock(Time)
    setattr(mocked_time, "year", 2023)
    setattr(mocked_time, "day", 178)
    data = FieldData(watering_amount_in_liters=50_000, watering_interval=5,
                     days_into_watering_interval=days_into_interval)
    data.watering_amount_in_mm = 5.0
    data.watering_occurs = watering_occurs
    data.current_water_deficit = water_deficit
    incorp = Field(field_data=data, manure_manager=MagicMock(ManureManager))

    actual = incorp._determine_watering_amount(rainfall, mocked_time.year, mocked_time.day, irrigation)
    if old_method:
        assert actual == irrigation
    else:
        if not watering_occurs:
            assert actual == 0.0
            assert incorp.field_data.days_into_watering_interval == days_into_interval
            assert incorp.field_data.annual_irrigation_water_use_total == 0
        elif days_into_interval == incorp.field_data.watering_interval:
            assert actual == max(0.0, water_deficit - rainfall)
            assert incorp.field_data.days_into_watering_interval == 0
            assert incorp.field_data.current_water_deficit == 5.0
            assert incorp.field_data.annual_irrigation_water_use_total == actual
        else:
            assert actual == 0.0
            assert incorp.field_data.days_into_watering_interval == days_into_interval + 1
            assert incorp.field_data.current_water_deficit == max(0.0, water_deficit - rainfall)
            assert incorp.field_data.annual_irrigation_water_use_total == 0


@pytest.mark.parametrize("precipitation,canopy_capacity,first_canopy_amount,second_canopy_amount,expected_return,"
                         "expected_first,expected_second", [
                             (13, 8, 2, 4, 3, 8, 8),  # Fills both pools with some leftover
                             (6, 7, 3, 2, 0, 7, 4),  # Fills one pool, puts some in second, none leftover
                             (14, 5, 7, 1, 12, 5, 5),  # Removes from one pool, fills other, some leftover
                             (3, 6, 8, 9, 8, 6, 6),  # Removes from both pools, lots left over
                             (5, 10, 3, 12, 2, 8, 10)  # Fills one pool as much as possible, removes excess from
                             # another
                         ]
                         )
def test_handle_water_in_crop_canopies(precipitation: float, canopy_capacity: float, first_canopy_amount: float,
                                       second_canopy_amount: float, expected_return: float, expected_first: float,
                                       expected_second: float) -> None:
    """Tests that water is properly added and removed from the crop canopies of field objects."""
    with patch("RUFAS.routines.field.crop.crop_data.CropData.water_canopy_storage_capacity",
               new_callable=PropertyMock, return_value=canopy_capacity):
        crop_data1 = CropData(canopy_water=first_canopy_amount)
        crop1 = Crop(crop_data1)
        crop_data2 = CropData(canopy_water=second_canopy_amount)
        crop2 = Crop(crop_data2)
        field = Field(manure_manager=MagicMock(ManureManager))
        field.crops = [crop1, crop2]

        actual = field._handle_water_in_crop_canopies(precipitation)
        assert actual == expected_return
        assert field.crops[0].data.canopy_water == expected_first
        assert field.crops[1].data.canopy_water == expected_second


@pytest.mark.parametrize("demand,canopy_water_1,canopy_water_2,expected_demand,expected_canopy_water1,"
                         "expected_canopy_water2", [
                             (14.5, 1.8, 2.3, 10.4, 0.0, 0.0),
                             (8.6, 4.7, 4.1, 0.0, 0.0, 0.2),
                             (9.5, 10.8, 5.7, 0.0, 1.3, 5.7)
                         ])
def test_evaporate_from_crop_canopies(demand: float, canopy_water_1: float, canopy_water_2: float,
                                      expected_demand: float, expected_canopy_water1: float,
                                      expected_canopy_water2: float) -> None:
    """Tests that the evapotranspirative demand is correctly reduced by the amounts of water evaporated."""
    data1 = CropData(canopy_water=canopy_water_1)
    crop1 = Crop(data1)
    data2 = CropData(canopy_water=canopy_water_2)
    crop2 = Crop(data2)
    field = Field(manure_manager=MagicMock(ManureManager))
    field.crops = [crop1, crop2]

    actual_demand = field._evaporate_from_crop_canopies(demand)
    assert pytest.approx(actual_demand) == expected_demand
    assert pytest.approx(expected_canopy_water1) == field.crops[0].data.canopy_water
    assert pytest.approx(expected_canopy_water2) == field.crops[1].data.canopy_water


@pytest.mark.parametrize("biomasses,expected", [
    ([30, 20, 14], 64),
    ([22.1], 22.1),
    ([], 0.0)
])
def test_determine_total_above_ground_biomass(biomasses: List[float], expected: float) -> None:
    """Tests that total above ground biomass on the field is correctly calculated."""
    field = Field(manure_manager=MagicMock(ManureManager))
    for biomass in biomasses:
        crop = Crop()
        crop.data.above_ground_biomass = biomass
        field.crops.append(crop)

    actual = field._determine_total_above_ground_biomass()
    assert actual == expected


@pytest.mark.parametrize("extraterrestrial_radiation,max_temp,min_temp,avg_temp,expected_avg,expected_result", [
    (100, 28, 10, 14, 14, 23.869749),
    (568, 20, 14, 18, 18, 88.123445),
    (568, 20, 14, None, 17, 85.661897),
    (80, 14, 0, 8, 8, 13.663381),
    (678.0098, 26.8896, 10.3339, 18.3345, 18.3345, 176.36657),
    (678.0098, 26.8896, 10.3339, -100000, -100000, 0.0)
])
def test_potential_evapotranspiration(extraterrestrial_radiation: float, max_temp: float, min_temp: float,
                                      avg_temp: float, expected_avg: float, expected_result) -> None:
    with patch("RUFAS.routines.field.field.field.Field._determine_latent_heat_vaporization",
               new_callable=MagicMock, return_value=1.3) as mocked_latent_heat:
        actual = Field._determine_potential_evapotranspiration(extraterrestrial_radiation, max_temp, min_temp, avg_temp)

        mocked_latent_heat.assert_called_once_with(expected_avg)
        assert pytest.approx(actual) == expected_result


@pytest.mark.parametrize("avg_temp", [
    12.86878,
    0,
    (-2.586948),
    20.4486,
])
def test_determine_latent_heat_vaporization(avg_temp):
    observe = Field._determine_latent_heat_vaporization(avg_temp)
    expect = 2.501 - (0.002361 * avg_temp)
    assert expect == observe


@pytest.mark.parametrize("above_ground_biomass,residue,snow_water,potential_evapotrans_adj,transpiration", [
    (800, 40, 0.3, 1.6, 0.9),  # arbitrary
    (1200, 300, 0.433, 2.4, 1.8),  # arbitrary
    (0, 800, 0.03, 0, 3.6),  # after harvest
    (800, 56, 0.84, 0.44, 0.23),  # snowy
    (0, 0, 0.22, 0.69, 0.45),  # empty field
    (400, 150, 0, 0.01, 0),  # dry conditions
    (500, 200, 0, 6.3, 4.5),  # wet conditions
    (300, 40, 2.33, 0.0, 0.0)
])
def test_determine_soil_evaporation_and_sublimation_adjusted(above_ground_biomass: float, residue: float,
                                                             snow_water: float, potential_evapotrans_adj: float,
                                                             transpiration: float) -> None:
    """Tests that the amount of soil evaporation and sublimation is calculated correctly."""
    with patch("RUFAS.routines.field.field.field.Field._determine_soil_cover_index", new_callable=MagicMock,
               return_value=1.3) as mocked_soil_cover_index:
        actual = Field._determine_soil_evaporation_and_sublimation_adjusted(above_ground_biomass, residue, snow_water,
                                                                            potential_evapotrans_adj, transpiration)
        if potential_evapotrans_adj == transpiration == 0.0:
            expected = 0.0
            mocked_soil_cover_index.assert_not_called()
        else:
            soil_evaporation = potential_evapotrans_adj * 1.3
            reduced_soil_evaporation = (soil_evaporation * potential_evapotrans_adj) / \
                                       (soil_evaporation + transpiration)
            expected = min(soil_evaporation, reduced_soil_evaporation)
            mocked_soil_cover_index.assert_called_once_with(above_ground_biomass, residue, snow_water)

        assert actual == expected


@pytest.mark.parametrize("above_ground_biomass,residue,snow_water", [
    (400, 65, 0.3),
    (800, 120, 0),
    (0, 0, 0),
    (1250, 800, 0.4999),
    (990, 200, 0.338),
    (400, 30, 0.51),
])
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
    field = Field(manure_manager=MagicMock(ManureManager))
    field.soil.data.do_annual_reset = MagicMock()
    field.field_data.perform_annual_field_reset = MagicMock()

    field.perform_annual_reset()

    field.soil.data.do_annual_reset.assert_called_once()
    field.field_data.perform_annual_field_reset.assert_called_once()


@pytest.mark.parametrize("events, day, year, not_today, is_today", [
    ([TillageEvent(10, 0.5, 0.3, 1997, 7), TillageEvent(10, 0.5, 0.3, 1998, 7), TillageEvent(10, 0.5, 0.3, 1999, 7)],
     7, 1998, [TillageEvent(10, 0.5, 0.3, 1997, 7), TillageEvent(10, 0.5, 0.3, 1999, 7)],
     [TillageEvent(10, 0.5, 0.3, 1998, 7)]),
    ([], 7, 1998, [], []),
    ([TillageEvent(10, 0.5, 0.3, 1997, 7), TillageEvent(10, 0.5, 0.3, 1999, 7), TillageEvent(10, 0.5, 0.3, 2023, 7)],
     7, 1998, [TillageEvent(10, 0.5, 0.3, 1997, 7), TillageEvent(10, 0.5, 0.3, 1999, 7),
               TillageEvent(10, 0.5, 0.3, 2023, 7)], []),
    ([TillageEvent(7, 0.5, 0.3, 1998, 7), TillageEvent(10, 0.5, 0.4, 1998, 7), TillageEvent(5, 0.5, 0.3, 1998, 7)],
     7, 1998, [], [TillageEvent(7, 0.5, 0.3, 1998, 7), TillageEvent(10, 0.5, 0.4, 1998, 7),
                   TillageEvent(5, 0.5, 0.3, 1998, 7)])
])
def test_check_tillage_schedule(events: List[TillageEvent], day: int, year: int,
                                not_today: List[TillageEvent], is_today: List[TillageEvent]) -> None:
    mocked_time = MagicMock(Time)
    setattr(mocked_time, "calendar_year", year)
    setattr(mocked_time, "day", day)

    field = Field(tillage_events=events, manure_manager=MagicMock(ManureManager))
    todays_count = len(is_today)
    field.tiller.till_soil = MagicMock()
    field._check_tillage_schedule(mocked_time)
    assert field.tillage_events == not_today

    assert field.tiller.till_soil.call_count == todays_count


# TODO: All field methods need to be tested in future PRs.


# --- Test FieldData methods ---
@pytest.mark.parametrize("liters,area", [
    (100, 2.3),
    (356, 4.556),
    (60, 1.8)
])
def test_liters_to_millimeters(liters: float, area: float) -> None:
    """Tests that the conversion from liters for evenly distributed millimeters is performed correctly."""
    actual = FieldData.convert_liters_to_millimeters(liters, area)
    expected = (liters * LITERS_TO_CUBIC_MILLIMETERS) / (area * HECTARES_TO_SQUARE_MILLIMETERS)
    assert actual == expected


@pytest.mark.parametrize("latitude,min_daylength,watering_amount,watering_interval", [
    (45.66, 12.5, 2000, 3),
    (37.445, 9.88, 7500, 7),
    (50.667, 10.334, 0, 5),
    (49.551, 12.65, 3500, 0)
])
def test_field_data_initialization(latitude: float, min_daylength: float, watering_amount: float,
                                   watering_interval: int) -> None:
    """Tests that FieldData objects are initialized correctly."""
    Dormancy.find_dormancy_threshold = MagicMock(return_value=14.5)
    Dormancy.find_threshold_daylength = MagicMock(return_value=10.22)
    FieldData.convert_liters_to_millimeters = MagicMock(return_value=0.8)

    data = FieldData(field_size=3, absolute_latitude=latitude, minimum_daylength=min_daylength,
                     watering_amount_in_liters=watering_amount, watering_interval=watering_interval)

    Dormancy.find_dormancy_threshold.assert_called_once_with(latitude)
    Dormancy.find_threshold_daylength.assert_called_once_with(min_daylength, 14.5)
    assert data.dormancy_threshold == 14.5
    assert data.dormancy_threshold_daylength == 10.22
    if watering_amount is not None and watering_amount != 0.0 and watering_interval is not None and \
            watering_interval != 0:
        FieldData.convert_liters_to_millimeters.assert_called_once_with(watering_amount, 3)
        assert data.watering_amount_in_mm == 0.8
        assert data.current_water_deficit == 0.8
        assert data.watering_occurs
    else:
        FieldData.convert_liters_to_millimeters.assert_not_called()
        assert data.watering_amount_in_mm == 0
        assert data.current_water_deficit == 0
        assert not data.watering_occurs


@pytest.mark.parametrize("watering_amount,interval", [
    (-1300, 13),
    (2000, -3)
])
def test_error_field_data_initialization(watering_amount: float, interval: int) -> None:
    """Tests that errors are correctly raised when FieldData is initialized with invalid values."""
    with pytest.raises(Exception) as e:
        FieldData(watering_amount_in_liters=watering_amount, watering_interval=interval)
    if watering_amount < 0:
        assert f"Expected watering amount to be >= 0, received '{watering_amount}'." == str(e.value)
    elif interval < 0:
        assert f"Expected watering interval to be >= 0, received '{interval}'." == str(e.value)


@pytest.mark.parametrize("field_name,field_size,day,year,watering_amount,expected_info_map,expected_value", [
    ("name_1", 100, 120, 1993, 135.6,
     {"prefix": "field='name_1'", "date": {"year": 1993, "day": 120}, "field_size": 100, "units": "mm"}, 135.6),
    ("name_2", 14.65, 3, 1996, 1.2,
     {"prefix": "field='name_2'", "date": {"year": 1996, "day": 3}, "field_size": 14.65, "units": "mm"}, 1.2),
    ("name_2", 14.65, 48, 2023, 1.2,
     {"prefix": "field='name_2'", "date": {"year": 2023, "day": 48}, "field_size": 14.65, "units": "mm"}, 1.2)
])
def test_record_field_watering(field_name: str, field_size: float, day: int, year: int, watering_amount: float,
                               expected_info_map: Dict, expected_value: Dict) -> None:
    field = Field(field_data=FieldData(name=field_name, field_size=field_size), manure_manager=MagicMock(ManureManager))
    field._record_field_watering(year=year, day=day, watering_amount=watering_amount)

    actual = om.variables_pool[f"field='{field_name}'.field_watering"]
    assert actual["info_maps"].__contains__(expected_info_map)
    assert actual["values"].__contains__(expected_value)


@pytest.mark.parametrize("annual_irrigation_water_use_total,expected", [
    (1500, 0),
    (063.25, 0),
    (0, 0)
])
def test_field_data_perform_annual_field_reset(annual_irrigation_water_use_total: float, expected: float) -> None:
    """Tests that annual variable was reset correctly."""
    data = FieldData(annual_irrigation_water_use_total=annual_irrigation_water_use_total)
    data.perform_annual_field_reset()
    assert expected == data.annual_irrigation_water_use_total

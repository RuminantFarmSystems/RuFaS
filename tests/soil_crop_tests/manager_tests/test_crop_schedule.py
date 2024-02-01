import pytest
from typing import List, Dict

from RUFAS.routines.field.crop.harvest_operations import HarvestOperation
from RUFAS.routines.field.manager.crop_schedule import CropSchedule
from RUFAS.routines.field.manager.events import PlantingEvent, HarvestEvent


@pytest.mark.parametrize("name,crop_ref,plant_years,plant_days,harvest_years,harvest_days,harvest_ops,heat_sched,"
                         "plant_skip,harvest_skip,pat_repeat,expected", [
                             ("test_1", "corn", [1990, 1991], [120], [1990, 1991], [255, 255],
                              ["harvest_kill", "harvest_kill"], False, 2, 2, 3,
                              {"plant_years": [1990, 1991], "plant_days": [120, 120], "harvest_years": [1990, 1991],
                               "harvest_days": [255, 255],
                               "harvest_ops": [HarvestOperation.HARVEST_KILL, HarvestOperation.HARVEST_KILL]}),
                             ("test_2", "beans", [1990, 1991, 1992], [120, 121, 121], [1990, 1991, 1992],
                              [255, 255, 260], ["harvest_only", "harvest_only", "harvest_kill"], True, 2, 4, 3,
                              {"plant_years": [1990, 1991, 1992], "plant_days": [120, 121, 121],
                               "harvest_years": [1990, 1991, 1992], "harvest_days": [255, 255, 260],
                               "harvest_ops": [HarvestOperation.HARVEST_ONLY, HarvestOperation.HARVEST_ONLY,
                                               HarvestOperation.HARVEST_KILL]}),
                             ("test_3", "greens", [1999], [130], [2000], [220], ["harvest_kill"], False, 0, 0, 10,
                              {"plant_years": [1999], "plant_days": [130], "harvest_years": [2000],
                               "harvest_days": [220], "harvest_ops": [HarvestOperation.HARVEST_KILL]})
                         ])
def test_crop_schedule_init(name: str, crop_ref: str, plant_years: List[int], plant_days: List[int],
                            harvest_years: List[int], harvest_days: List[int], harvest_ops: List[str],
                            heat_sched: bool, plant_skip: int, harvest_skip: int, pat_repeat: int,
                            expected: Dict) -> None:
    """Tests that CropSchedule's get initialized correctly."""
    crop_schedule = CropSchedule(name, crop_ref, plant_years, plant_days, harvest_years, harvest_days, harvest_ops,
                                 heat_sched, plant_skip, harvest_skip, pat_repeat)
    assert crop_schedule.name == name
    assert crop_schedule.crop_reference == crop_ref
    assert crop_schedule.planting_years == expected.get("plant_years")
    assert crop_schedule.planting_days == expected.get("plant_days")
    assert crop_schedule.harvest_years == expected.get("harvest_years")
    assert crop_schedule.harvest_days == expected.get("harvest_days")
    assert crop_schedule.harvest_operations == expected.get("harvest_ops")
    assert crop_schedule.heat_scheduled == heat_sched
    assert crop_schedule.pattern_skip == plant_skip
    print(f"{crop_schedule.planting_skip} {plant_skip}")
    assert crop_schedule.planting_skip == plant_skip
    assert crop_schedule.harvesting_skip == harvest_skip
    assert crop_schedule.pattern_repeat == pat_repeat


@pytest.mark.parametrize("name,years,days,expected", [
    ("test_1", [1990, 1989], [], "'test_1': expected all years to be > 0 and in non-descending order, received "
                                 "'[1990, 1989]'."),
    ("test_2", [1998, 1999, 2000], [200, 200, 367], "'test_2': expected all planting days to be in range [1, 366], "
                                                    "received '[200, 200, 367]'."),
    ("test_3", [1997, 1998], [90, 120, 90], "'test_3': expected number of planting years and days to be the same, "
                                            "received '[1997, 1998]' years and '[90, 120, 90]' days.")
])
def test_validate_planting_parameters(name: str, years: List[int], days: List[int], expected: str) -> None:
    """Tests that the errors are raised properly when crop planting parameters are invalid."""
    with pytest.raises(ValueError) as e:
        test = CropSchedule(name, "test_crop", years, days, [2000], [240], ["harvest_kill"], False, 1, 1)
        test._validate_planting_parameters()
    assert str(e.value) == expected


@pytest.mark.parametrize("name,years,days,operations,expected", [
    ("test_1", [1996, 1993], [200], ["harvest_kill"],
     "'test_1': expected all harvest years to be > 0 and in non-descending order, received '[1996, 1993]'."),
    ("test_2", [1999, 2000], [200, 0], ["harvest_kill"],
     "'test_2': expected all harvest days to be in range [1, 366], received '[200, 0]'."),
    ("test_3", [1998, 1999, 2000], [200, 200], ["harvest_only", "harvest_kill"],
     "'test_3': expected number of values for harvest years, days, and operations to be equal, received "
     "'[1998, 1999, 2000]' years, '[200, 200]' days, and '[<HarvestOperation.HARVEST_ONLY: 'harvest_only'>, "
     "<HarvestOperation.HARVEST_KILL: 'harvest_kill'>]' operations."),
    ("test_4", [1998, 1999, 1999], [200, 200, 240], ["harvest_only", "harvest_kill", "harvest_only"],
     "'test_4': expected the final harvest operation to be the only one that kills the crop, received "
     "'[<HarvestOperation.HARVEST_ONLY: 'harvest_only'>, <HarvestOperation.HARVEST_KILL: 'harvest_kill'>, "
     "<HarvestOperation.HARVEST_ONLY: 'harvest_only'>]'.")
])
def test_validate_harvest_parameters(name: str, years: List[int], days: List[int], operations: List[str],
                                     expected: str) -> None:
    """Tests that harvest schedule parameters are valid."""
    with pytest.raises(ValueError) as e:
        test = CropSchedule(name, "test_crop", [1990], [130], years, days, operations, False, 1, 1)
        test._validate_harvest_parameters()
    assert str(e.value) == expected


@pytest.mark.parametrize("years,days,heat_scheduled,skip,repeat,expected", [
    ([1, 3, 4], [120, 100, 100], False, 1, 1, [PlantingEvent("test_crop", 1, 120, False),
                                               PlantingEvent("test_crop", 3, 100, False),
                                               PlantingEvent("test_crop", 4, 100, False),
                                               PlantingEvent("test_crop", 6, 120, False),
                                               PlantingEvent("test_crop", 8, 100, False),
                                               PlantingEvent("test_crop", 9, 100, False)]),
    ([2, 4], [115, 115], True, 2, 2, [PlantingEvent("test_crop", 2, 115, True),
                                      PlantingEvent("test_crop", 4, 115, True),
                                      PlantingEvent("test_crop", 7, 115, True),
                                      PlantingEvent("test_crop", 9, 115, True),
                                      PlantingEvent("test_crop", 12, 115, True),
                                      PlantingEvent("test_crop", 14, 115, True)]),
    ([1, 2, 5], [120, 120, 110], False, 2, 0, [PlantingEvent("test_crop", 1, 120, False),
                                               PlantingEvent("test_crop", 2, 120, False),
                                               PlantingEvent("test_crop", 5, 110, False)])
])
def test_generate_planting_events(years: List[int], days: List[int], heat_scheduled: bool, skip: int,
                                  repeat: int, expected: List[PlantingEvent]) -> None:
    """Tests that planting events are correctly generated by CropSchedule objects."""
    crop_sched = CropSchedule("test_name", "test_crop", years, days, [1], [240], ["harvest_kill"], heat_scheduled, skip,
                              0, repeat)
    actual = crop_sched.generate_planting_events()
    assert actual == expected


@pytest.mark.parametrize("years,days,harvest_ops,heat_scheduled,skip,repeat,expected", [
    ([1, 2, 6], [245, 245, 240], ["harvest_only", "harvest_only", "harvest_kill"], False, 1, 1,
     [HarvestEvent("test", 1, 245, HarvestOperation.HARVEST_ONLY),
      HarvestEvent("test", 2, 245, HarvestOperation.HARVEST_ONLY),
      HarvestEvent("test", 6, 240, HarvestOperation.HARVEST_KILL),
      HarvestEvent("test", 8, 245, HarvestOperation.HARVEST_ONLY),
      HarvestEvent("test", 9, 245, HarvestOperation.HARVEST_ONLY),
      HarvestEvent("test", 13, 240, HarvestOperation.HARVEST_KILL)]),
    ([1, 1], [200, 260], ["harvest_only", "harvest_kill"], False, 2, 2,
     [HarvestEvent("test", 1, 200, HarvestOperation.HARVEST_ONLY),
      HarvestEvent("test", 1, 260, HarvestOperation.HARVEST_KILL),
      HarvestEvent("test", 4, 200, HarvestOperation.HARVEST_ONLY),
      HarvestEvent("test", 4, 260, HarvestOperation.HARVEST_KILL),
      HarvestEvent("test", 7, 200, HarvestOperation.HARVEST_ONLY),
      HarvestEvent("test", 7, 260, HarvestOperation.HARVEST_KILL)]),
    ([1, 2, 3], [240, 240, 240], ["harvest_only", "harvest_only", "harvest_kill"], True, 1, 2,
     [HarvestEvent("test", 3, 240, HarvestOperation.HARVEST_KILL),
      HarvestEvent("test", 7, 240, HarvestOperation.HARVEST_KILL),
      HarvestEvent("test", 11, 240, HarvestOperation.HARVEST_KILL),
      ])
])
def test_generate_harvest_events(years: List[int], days: List[int], harvest_ops: List[str], heat_scheduled: bool,
                                 skip: int, repeat: int, expected: List[HarvestEvent]) -> None:
    """Tests that harvest events are correctly generated by CropSchedule objects."""
    crop_sched = CropSchedule("test_name", "test", [1], [120], years, days, harvest_ops, heat_scheduled, 0, skip,
                              repeat)
    actual = crop_sched.generate_harvest_events()
    assert actual == expected

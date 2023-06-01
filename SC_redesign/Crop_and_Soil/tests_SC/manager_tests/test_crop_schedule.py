import pytest
from typing import List, Dict, Any

from SC_redesign.Crop_and_Soil.manager.crop_schedule import CropSchedule
from SC_redesign.Crop_and_Soil.manager.events import PlantingEvent, HarvestEvent


@pytest.mark.parametrize("crop_ref,plant_years,plant_days,harvest_years,harvest_days,harvest_ops,heat_sched,pat_skip,"
                         "pat_repeat,expected", [
                             ("corn", [1990, 1991], 120, [1990, 1991], [255, 255], ["default", "default"], False, 2, 3,
                              {"plant_years": [1990, 1991], "plant_days": [120, 120],
                               "harvest_years": [1990, 1991],
                               "harvest_days": [255, 255],
                               "harvest_ops": ["default", "default"]}),
                             ("beans", [1990, 1991, 1992], [120, 121, 121], [1990, 1991, 1992], [255, 255, 260],
                              ["no_kill", "no_kill", "default"], True, 2, 3,
                              {"plant_years": [1990, 1991, 1992], "plant_days": [120, 121, 121],
                               "harvest_years": [1990, 1991, 1992],
                               "harvest_days": [255, 255, 260],
                               "harvest_ops": ["no_kill", "no_kill", "default"]}),
                             ("greens", 1999, 130, 2000, 220, "default", False, 0, 10, {"plant_years": [1999],
                                                                                        "plant_days": [130],
                                                                                        "harvest_years": [2000],
                                                                                        "harvest_days": [220],
                                                                                        "harvest_ops": ["default"]})
                         ])
def test_crop_schedule_init(crop_ref: str, plant_years: int | List[int], plant_days: int | List[int],
                            harvest_years: int | List[int], harvest_days: int | List[int], harvest_ops: str | List[str],
                            heat_sched: bool, pat_skip: int, pat_repeat: int, expected: Dict) -> None:
    """Tests that CropSchedule's get initialized correctly."""
    crop_schedule = CropSchedule(crop_ref, plant_years, plant_days, harvest_years, harvest_days, harvest_ops,
                                 heat_sched, pat_skip, pat_repeat)
    assert crop_schedule.crop_reference == crop_ref
    assert crop_schedule.planting_years == expected.get("plant_years")
    assert crop_schedule.planting_days == expected.get("plant_days")
    assert crop_schedule.harvest_years == expected.get("harvest_years")
    assert crop_schedule.harvest_days == expected.get("harvest_days")
    assert crop_schedule.harvest_operations == expected.get("harvest_ops")
    assert crop_schedule.heat_scheduled == heat_sched
    assert crop_schedule.pattern_skip == pat_skip
    assert crop_schedule.pattern_repeat == pat_repeat


@pytest.mark.parametrize("plant_years,plant_days,harvest_years,harvest_days,harvest_ops,pat_skip,pat_repeat,expected", [
    ([1] * 3, [1] * 2, [1] * 3, [1] * 3, ["default"] * 3, 0, 3,
     "Number of years that crops are planted in and days crops are planted on must be equal."),
    ([1] * 2, [1] * 2, [1] * 3, [1] * 2, ["default"] * 3, 0, 3,
     "Number of values for harvest years, days, and operations must be equal."),
    ([1] * 2, [1] * 2, [1] * 3, [1] * 3, ["default"] * 3, -1, 3, "Expected pattern skip to be >= 0, received '-1'."),
    ([1] * 2, [1] * 2, [1] * 3, [1] * 3, ["default"] * 3, 3, -1, "Expected pattern repeat to be >= 0, received '-1'."),
    ([1], [1], [1] * 3, [1] * 3, ["no_kill", "default", "no_kill"], 0, 0, "Expected the final harvest operation to be "
                                                                          "the only one that kills the crop, received "
                                                                          "'['no_kill', 'default', 'no_kill']'.")
])
def test_crop_schedule_init_error(plant_years: int | List[int], plant_days: int | List[int],
                                  harvest_years: int | List[int], harvest_days: int | List[int],
                                  harvest_ops: str | List[str], pat_skip: int, pat_repeat: int, expected: str) -> None:
    """Tests that errors are correctly raised when invalid input is passed."""
    with pytest.raises(ValueError) as e:
        CropSchedule("test", plant_years, plant_days, harvest_years, harvest_days, harvest_ops, False, pat_skip,
                     pat_repeat)
    assert str(e.value) == expected


@pytest.mark.parametrize("years,days,heat_scheduled,skip,repeat,expected", [
    ([1, 3, 4], [120, 100, 100], False, 1, 1, [PlantingEvent("test", 1, 120, False),
                                               PlantingEvent("test", 3, 100, False),
                                               PlantingEvent("test", 4, 100, False),
                                               PlantingEvent("test", 6, 120, False),
                                               PlantingEvent("test", 8, 100, False),
                                               PlantingEvent("test", 9, 100, False)]),
    ([2, 4], [115, 115], True, 2, 2, [PlantingEvent("test", 2, 115, True), PlantingEvent("test", 4, 115, True),
                                      PlantingEvent("test", 7, 115, True), PlantingEvent("test", 9, 115, True),
                                      PlantingEvent("test", 12, 115, True), PlantingEvent("test", 14, 115, True)]),
    ([1, 2, 5], [120, 120, 110], False, 2, 0, [PlantingEvent("test", 1, 120, False),
                                               PlantingEvent("test", 2, 120, False),
                                               PlantingEvent("test", 5, 110, False)])
])
def test_generate_planting_events(years: List[int], days: List[int], heat_scheduled: bool, skip: int,
                                  repeat: int, expected: List[PlantingEvent]) -> None:
    """Tests that planting events are correctly generated by CropSchedule objects."""
    crop_sched = CropSchedule("test", years, days, [1], [240], ["default"], heat_scheduled, skip, repeat)
    actual = crop_sched.generate_planting_events()
    assert actual == expected


@pytest.mark.parametrize("years,days,harvest_ops,heat_scheduled,skip,repeat,expected", [
    ([1, 2, 6], [245, 245, 240], ["no_kill", "no_kill", "default"], False, 1, 1,
     [HarvestEvent("test", 1, 245, "no_kill"), HarvestEvent("test", 2, 245, "no_kill"),
      HarvestEvent("test", 6, 240, "default"), HarvestEvent("test", 8, 245, "no_kill"),
      HarvestEvent("test", 9, 245, "no_kill"), HarvestEvent("test", 13, 240, "default")]),
    ([1, 1], [200, 260], ["no_kill", "default"], False, 2, 2, [HarvestEvent("test", 1, 200, "no_kill"),
                                                               HarvestEvent("test", 1, 260, "default"),
                                                               HarvestEvent("test", 4, 200, "no_kill"),
                                                               HarvestEvent("test", 4, 260, "default"),
                                                               HarvestEvent("test", 7, 200, "no_kill"),
                                                               HarvestEvent("test", 7, 260, "default")]),
    ([1, 2, 3], [240, 240, 240], ["no_kill", "no_kill", "default"], True, 1, 2,
     [HarvestEvent("test", 3, 240, "default"), HarvestEvent("test", 7, 240, "default"),
      HarvestEvent("test", 11, 240, "default")])
])
def test_generate_harvest_events(years: List[int], days: List[int], harvest_ops: List[str], heat_scheduled: bool,
                                 skip: int, repeat: int, expected: List[HarvestEvent]) -> None:
    """Tests that harvest events are correctly generated by CropSchedule objects."""
    crop_sched = CropSchedule("test", [1], [120], years, days, harvest_ops, heat_scheduled, skip, repeat)
    actual = crop_sched.generate_harvest_events()
    assert actual == expected


@pytest.mark.parametrize("to_be_converted,expected", [
    (120, [120]),
    (["default"], ["default"])
])
def test_convert_to_list(to_be_converted: Any, expected: List):
    """Test that data is correctly converted to be in a list."""
    actual = CropSchedule._convert_to_list(to_be_converted)
    assert actual == expected

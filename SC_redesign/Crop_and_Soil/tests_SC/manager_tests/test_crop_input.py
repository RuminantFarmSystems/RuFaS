from typing import Any, Tuple

import pytest

from SC_redesign.Crop_and_Soil.crop.harvest_operations import HarvestOperation
from SC_redesign.Crop_and_Soil.manager.crop_input import CropScheduleSpec


@pytest.mark.parametrize("x,expect", [
    (1, (1,)),
    ([1], (1,)),
    ([1, 2, 3], (1, 2, 3)),
    ([(1, 2, 3), (1, 2, 3)]),
    ("a", ("a",)),
    (["a", "b", "c"], ("a", "b", "c")),
    ([[1, 2], 1, 3], ([1, 2], 1, 3)),
    ("ham_and_eggs", ("ham_and_eggs",)),
    (["spam", "eggs"], ("spam", "eggs"))
])
def test_convert_to_tuple(x: Any, expect: Tuple):
    """check that input are correctly converted to tuples"""
    assert CropScheduleSpec._convert_to_tuple(x) == expect


def test_crop_schedule_spec() -> None:
    """test that the crop schedule specification creates the expected structure for a number of different use cases"""
    case_1 = CropScheduleSpec(planting_years=1, planting_days=120, harvest_years=1, harvest_days=220,
                              harvest_operations="default")
    assert case_1.planting_years == (1,)
    assert case_1.planting_days == (120,)
    assert case_1.harvest_years == (1,)
    assert case_1.harvest_days == (220,)
    assert case_1.harvest_operations == (HarvestOperation.HARVEST,)

    case_2 = CropScheduleSpec(planting_years=(1, 2, 3), planting_days=(120, 115, 123),
                              harvest_years=(1, 2, 3), harvest_days=(220, 220, 238),
                              harvest_operations=("no_kill", "no_kill", "default"))
    assert case_2.planting_years == (1, 2, 3)
    assert case_2.planting_days == (120, 115, 123)
    assert case_2.harvest_years == (1, 2, 3)
    assert case_2.harvest_days == (220, 220, 238)
    assert case_2.harvest_operations == (HarvestOperation.HARVEST_NOKILL, HarvestOperation.HARVEST_NOKILL,
                                         HarvestOperation.HARVEST)

    case_3 = CropScheduleSpec(planting_years=(1, 2, 3), planting_days=120,
                              harvest_years=(1, 2, 3), harvest_days=220,
                              harvest_operations="no_kill")
    assert case_3.planting_years == (1, 2, 3)
    assert case_3.planting_days == (120, 120, 120)
    assert case_3.harvest_years == (1, 2, 3)
    assert case_3.harvest_days == (220, 220, 220)
    assert case_3.harvest_operations == tuple([HarvestOperation.HARVEST_NOKILL]*3)

    case_4 = CropScheduleSpec(planting_years=1, planting_days=300, harvest_years=2, harvest_days=115,
                              harvest_operations="default", pattern_skip=0, pattern_repeat=4)
    assert case_4.planting_years == (1, 2, 3, 4, 5)
    assert case_4.planting_days == (300,)*5
    assert case_4.harvest_years == (2, 3, 4, 5, 6)
    assert case_4.harvest_days == (115,)*5
    assert case_4.harvest_operations == tuple([HarvestOperation.HARVEST]*5)

    case_5 = CropScheduleSpec(planting_years=[1, 2], planting_days=[115, 120],
                              harvest_years=[1, 2], harvest_days=[[200, 295], 220],
                              pattern_repeat=1)
    assert case_5.harvest_years == (1, 2, 3, 4)
    assert case_5.harvest_days == ([200, 295], 220, [200, 295], 220)

    case_6 = CropScheduleSpec(planting_years=[1, 3, 8], planting_days=120, harvest_years=[1, 3, 8],
                              pattern_repeat=2, pattern_skip=5)
    assert case_6.planting_years == (1, 3, 8, 14, 16, 21, 27, 29, 34)

    for case in (case_1, case_2, case_3, case_4, case_5, case_6):
        assert len(case.planting_years) == len(case.planting_days) == len(case.harvest_years) == \
               len(case.harvest_days) == len(case.harvest_operations)

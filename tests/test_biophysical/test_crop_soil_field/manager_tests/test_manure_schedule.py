from typing import List

import pytest

from RUFAS.data_structures.events import ManureEvent
from RUFAS.data_structures.manure_supplement_methods import ManureSupplementMethod
from RUFAS.biophysical.field.manager.manure_schedule import ManureSchedule
from RUFAS.data_structures.manure_types import ManureType


@pytest.mark.parametrize(
    "name,years,days,nitrogen,phosphorus,manure_type,field_coverage,depths,remainder_fracs,expected",
    [
        (
            "test_1",
            [1990, 1989],
            [100],
            [15],
            [15],
            [ManureType.LIQUID],
            [0.75],
            [0.0],
            [1.0],
            "'test_1': expected all years to be > 0 and in non-descending order, received '[1990, 1989]'.",
        ),
        (
            "test_2",
            [1990],
            [0],
            [15],
            [15],
            [ManureType.LIQUID],
            [0.75],
            [0.0],
            [1.0],
            "'test_2': expected all days to be in range [1, 366], received '[0]'.",
        ),
        (
            "test_3",
            [1990],
            [100],
            [-15.0],
            [15],
            [ManureType.LIQUID],
            [0.75],
            [0.0],
            [1.0],
            "'test_3': expected all nitrogen masses to be in >= 0, received '[-15.0]'.",
        ),
        (
            "test_4",
            [1990, 1993],
            [110],
            [15],
            [-10],
            [ManureType.LIQUID],
            [0.75],
            [0.0],
            [1.0],
            "'test_4': expected all phosphorus masses to be in >= 0, received '[-10, -10]'.",
        ),
        (
            "test_5",
            [1991],
            [100],
            [15],
            [15],
            [ManureType.LIQUID],
            [1.05],
            [0.0],
            [1.0],
            "'test_5': expected all field coverages to be in range [0.0, 1.0], received " "'[1.05]'.",
        ),
        (
            "test_6",
            [1994],
            [200],
            [15],
            [15],
            [ManureType.LIQUID],
            [0.75],
            [-15.0],
            [0.85],
            "'test_6': expected all manure application depths to be in >= 0, received '[-15.0]'.",
        ),
        (
            "test_7",
            [1990, 1994],
            [120],
            [15],
            [20],
            [ManureType.LIQUID],
            [0.8],
            [20],
            [-0.15],
            "'test_7': expected all surface remainder fractions to be in range [0.0, "
            "1.0], received '[-0.15, -0.15]'.",
        ),
        (
            "test_8",
            [1990, 1990, 1993],
            [120, 140],
            [20],
            [15, 10, 20],
            [ManureType.LIQUID],
            [0.8, 0.9],
            [0.0],
            [1.0],
            "'test_8':  Mismatch in length of parameters. Provided parameters are: "
            "years=[1990, 1990, 1993], days=[120, 140], nitrogen_masses=[20, 20, 20], "
            "phosphorus_masses=[15, 10, 20], application_depths=[0.0, 0.0, 0.0], "
            "surface_remainder_fractions=[1.0, 1.0, 1.0], "
            "manure_types=[<ManureType.LIQUID: 'liquid'>, <ManureType.LIQUID: 'liquid'>, "
            "<ManureType.LIQUID: 'liquid'>], "
            "manure_supplement_methods=[<ManureSupplementMethod.NONE: 'none'>, "
            "<ManureSupplementMethod.NONE: 'none'>, <ManureSupplementMethod.NONE: "
            "'none'>]. Lengths are: {'years': 3, 'days': 2, 'nitrogen_masses': 3, "
            "'phosphorus_masses': 3, 'application_depths': 3, "
            "'surface_remainder_fractions': 3, 'manure_types': 3, "
            "'manure_supplement_methods': 3}.",
        ),
        (
            "test_9",
            [1990],
            [100],
            [15],
            [15],
            ["ManureType.INVALID"],
            [0.75],
            [0.0],
            [1.0],
            "'test_9': expected all manure types to be valid ManureTypes, received '['ManureType.INVALID']'.",
        ),
    ],
)
def test_validate_manure_parameters(
    name: str,
    years: list[int],
    days: list[int],
    nitrogen: list[float],
    phosphorus: list[float],
    manure_type: list[ManureType],
    field_coverage: list[float],
    depths: list[float],
    remainder_fracs: list[float],
    expected: str,
) -> None:
    """Tests that invalid input is caught and raised with the correct error message in the init function."""
    with pytest.raises(ValueError) as e:
        ManureSchedule(
            name,
            years,
            days,
            nitrogen,
            phosphorus,
            manure_type,
            [ManureSupplementMethod.NONE],
            field_coverage,
            depths,
            remainder_fracs,
            1,
            1,
        )
    assert str(e.value) == expected


@pytest.mark.parametrize(
    "years,days,nitrogen,phosphorus,manure_type,manure_supplement_method,coverage,depth,surface_frac,skip,repeat,"
    "expected",
    [
        (
            [1990, 1992],
            [100],
            [20],
            [20, 25],
            [ManureType.LIQUID],
            [ManureSupplementMethod.NONE],
            [0.8],
            [0],
            [1.0],
            1,
            1,
            [
                ManureEvent(20, 20, ManureType.LIQUID, ManureSupplementMethod.NONE, 0.8, 0, 1.0, 1990, 100),
                ManureEvent(20, 25, ManureType.LIQUID, ManureSupplementMethod.NONE, 0.8, 0, 1.0, 1992, 100),
                ManureEvent(20, 20, ManureType.LIQUID, ManureSupplementMethod.NONE, 0.8, 0, 1.0, 1994, 100),
                ManureEvent(20, 25, ManureType.LIQUID, ManureSupplementMethod.NONE, 0.8, 0, 1.0, 1996, 100),
            ],
        ),
        (
            [1990, 1990],
            [100, 200],
            [25, 10],
            [5, 5],
            [ManureType.LIQUID],
            [ManureSupplementMethod.NONE],
            [0.8, 0.6],
            [15, 0],
            [0.3, 1.0],
            0,
            2,
            [
                ManureEvent(25, 5, ManureType.LIQUID, ManureSupplementMethod.NONE, 0.8, 15, 0.3, 1990, 100),
                ManureEvent(10, 5, ManureType.LIQUID, ManureSupplementMethod.NONE, 0.6, 0, 1.0, 1990, 200),
                ManureEvent(25, 5, ManureType.LIQUID, ManureSupplementMethod.NONE, 0.8, 15, 0.3, 1991, 100),
                ManureEvent(10, 5, ManureType.LIQUID, ManureSupplementMethod.NONE, 0.6, 0, 1.0, 1991, 200),
                ManureEvent(25, 5, ManureType.LIQUID, ManureSupplementMethod.NONE, 0.8, 15, 0.3, 1992, 100),
                ManureEvent(10, 5, ManureType.LIQUID, ManureSupplementMethod.NONE, 0.6, 0, 1.0, 1992, 200),
            ],
        ),
        (
            [1998],
            [115],
            [27],
            [22],
            [ManureType.LIQUID],
            [ManureSupplementMethod.NONE],
            [0.85],
            [0],
            [1.0],
            0,
            6,
            [
                ManureEvent(27, 22, ManureType.LIQUID, ManureSupplementMethod.NONE, 0.85, 0, 1.0, 1998, 115),
                ManureEvent(27, 22, ManureType.LIQUID, ManureSupplementMethod.NONE, 0.85, 0, 1.0, 1999, 115),
                ManureEvent(27, 22, ManureType.LIQUID, ManureSupplementMethod.NONE, 0.85, 0, 1.0, 2000, 115),
                ManureEvent(27, 22, ManureType.LIQUID, ManureSupplementMethod.NONE, 0.85, 0, 1.0, 2001, 115),
                ManureEvent(27, 22, ManureType.LIQUID, ManureSupplementMethod.NONE, 0.85, 0, 1.0, 2002, 115),
                ManureEvent(27, 22, ManureType.LIQUID, ManureSupplementMethod.NONE, 0.85, 0, 1.0, 2003, 115),
                ManureEvent(27, 22, ManureType.LIQUID, ManureSupplementMethod.NONE, 0.85, 0, 1.0, 2004, 115),
            ],
        ),
        (
            [1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999],
            [95, 94, 100, 95, 96, 89, 90, 93],
            [18],
            [10],
            [ManureType.LIQUID],
            [ManureSupplementMethod.NONE],
            [0.9],
            [30],
            [0.7],
            0,
            0,
            [
                ManureEvent(18, 10, ManureType.LIQUID, ManureSupplementMethod.NONE, 0.9, 30, 0.7, 1992, 95),
                ManureEvent(18, 10, ManureType.LIQUID, ManureSupplementMethod.NONE, 0.9, 30, 0.7, 1993, 94),
                ManureEvent(18, 10, ManureType.LIQUID, ManureSupplementMethod.NONE, 0.9, 30, 0.7, 1994, 100),
                ManureEvent(18, 10, ManureType.LIQUID, ManureSupplementMethod.NONE, 0.9, 30, 0.7, 1995, 95),
                ManureEvent(18, 10, ManureType.LIQUID, ManureSupplementMethod.NONE, 0.9, 30, 0.7, 1996, 96),
                ManureEvent(18, 10, ManureType.LIQUID, ManureSupplementMethod.NONE, 0.9, 30, 0.7, 1997, 89),
                ManureEvent(18, 10, ManureType.LIQUID, ManureSupplementMethod.NONE, 0.9, 30, 0.7, 1998, 90),
                ManureEvent(18, 10, ManureType.LIQUID, ManureSupplementMethod.NONE, 0.9, 30, 0.7, 1999, 93),
            ],
        ),
    ],
)
def test_generate_manure_events(
    years: List[int],
    days: List[int],
    nitrogen: List[float],
    phosphorus: List[float],
    manure_type: List[ManureType],
    manure_supplement_method: list[ManureSupplementMethod],
    coverage: List[float],
    depth: List[float],
    surface_frac: List[float],
    skip: int,
    repeat: int,
    expected: List[ManureEvent],
) -> None:
    """Tests that a full list of ManureEvents is correctly generated by the ManureSchedule."""
    man_sched = ManureSchedule(
        "test",
        years,
        days,
        nitrogen,
        phosphorus,
        manure_type,
        manure_supplement_method,
        coverage,
        depth,
        surface_frac,
        skip,
        repeat,
    )
    actual = man_sched.generate_manure_events()
    assert actual == expected

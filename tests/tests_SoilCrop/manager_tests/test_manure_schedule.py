import pytest
from typing import List, Union

from SC_redesign.Crop_and_Soil.manager.manure_schedule import ManureSchedule
from SC_redesign.Crop_and_Soil.manager.events import ManureEvent


@pytest.mark.parametrize("values,expected", [
    ([1, 3, 4], True),
    ([0.0, 1.2, 3.8], True),
    ([], True),
    ([-0.1, 0.1], False),
    ([-2, -4], False)
])
def test_determine_if_all_non_negative_values(values: List[Union[int, float]], expected: bool) -> None:
    """Tests that lists are correctly checked for negative values."""
    actual = ManureSchedule._determine_if_all_non_negative_values(values)
    assert actual == expected


@pytest.mark.parametrize("name,years,days,nitrogen,phosphorus,field_coverage,depths,remainder_fracs,expected", [
    ("test_1", [1990, 1989], [100], [15], [15], [0.75], [0.0], [1.0],
     "'test_1': expected all years to be > 0 and in non-descending order, received '[1990, 1989]'."),
    ("test_2", [1990], [0], [15], [15], [0.75], [0.0], [1.0],
     "'test_2': expected all days to be in range [1, 366], received '[0]'."),
    ("test_3", [1990], [100], [-15.0], [15], [0.75], [0.0], [1.0],
     "'test_3': expected all nitrogen masses to be >= 0, received '[-15.0]'."),
    ("test_4", [1990, 1993], [110], [15], [-10], [0.75], [0.0], [1.0],
     "'test_4': expected all phosphorus masses to be >= 0, received '[-10, -10]'."),
    ("test_5", [1991], [100], [15], [15], [1.05], [0.0], [1.0],
     "'test_5': expected all field coverage fractions to be in the range [0.0, 1.0], received '[1.05]'."),
    ("test_6", [1994], [200], [15], [15], [0.75], [-15.0], [0.85],
     "'test_6': expected all manure application depths to be >= 0, received '[-15.0]'."),
    ("test_7", [1990, 1994], [120], [15], [20], [0.8], [20], [-0.15],
     "'test_7': expected all surface remainder fractions to be in the range [0.0, 1.0], received '[-0.15, -0.15]'."),
    ("test_8", [1990, 1990, 1993], [120, 140], [20], [15, 10, 20], [0.8, 0.9], [0.0], [1.0],
     "'test_8': expected equal number of manure application parameters, received '[1990, 1990, 1993]' years, "
     "'[120, 140]' days, '[20, 20, 20]' nitrogen masses, '[15, 10, 20]' phosphorus masses, '[0.8, 0.9]' field coverage "
     "fractions, '[0.0, 0.0, 0.0]' application depths, and '[1.0, 1.0, 1.0]' surface remainder fractions.")
])
def test_validate_manure_parameters(name: str, years: List[int], days: List[int], nitrogen: List[float],
                                    phosphorus: List[float], field_coverage: List[float], depths: List[float],
                                    remainder_fracs: List[float], expected: str) -> None:
    """Tests that invalid input is caught and raised with the correct error message in the init function."""
    with pytest.raises(ValueError) as e:
        ManureSchedule(name, years, days, nitrogen, phosphorus, field_coverage, depths, remainder_fracs, 1, 1)
    assert str(e.value) == expected


@pytest.mark.parametrize("years,days,nitrogen,phosphorus,coverage,depth,surface_frac,skip,repeat,expected", [
    ([1990, 1992], [100], [20], [20, 25], [0.8], [0], [1.0], 1, 1, [
        ManureEvent(1990, 100, 20, 20, 0.8, 0, 1.0), ManureEvent(1992, 100, 20, 25, 0.8, 0, 1.0),
        ManureEvent(1994, 100, 20, 20, 0.8, 0, 1.0), ManureEvent(1996, 100, 20, 25, 0.8, 0, 1.0)
    ]),
    ([1990, 1990], [100, 200], [25, 10], [5, 5], [0.8, 0.6], [15, 0], [0.3, 1.0], 0, 2, [
        ManureEvent(1990, 100, 25, 5, 0.8, 15, 0.3), ManureEvent(1990, 200, 10, 5, 0.6, 0, 1.0),
        ManureEvent(1991, 100, 25, 5, 0.8, 15, 0.3), ManureEvent(1991, 200, 10, 5, 0.6, 0, 1.0),
        ManureEvent(1992, 100, 25, 5, 0.8, 15, 0.3), ManureEvent(1992, 200, 10, 5, 0.6, 0, 1.0)
    ]),
    ([1998], [115], [27], [22], [0.85], [0], [1.0], 0, 6, [
        ManureEvent(1998, 115, 27, 22, 0.85, 0, 1.0), ManureEvent(1999, 115, 27, 22, 0.85, 0, 1.0),
        ManureEvent(2000, 115, 27, 22, 0.85, 0, 1.0), ManureEvent(2001, 115, 27, 22, 0.85, 0, 1.0),
        ManureEvent(2002, 115, 27, 22, 0.85, 0, 1.0), ManureEvent(2003, 115, 27, 22, 0.85, 0, 1.0),
        ManureEvent(2004, 115, 27, 22, 0.85, 0, 1.0)
    ]),
    ([1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999], [95, 94, 100, 95, 96, 89, 90, 93], [18], [10], [0.9], [30],
     [0.7], 0, 0, [
        ManureEvent(1992, 95, 18, 10, 0.9, 30, 0.7), ManureEvent(1993, 94, 18, 10, 0.9, 30, 0.7),
        ManureEvent(1994, 100, 18, 10, 0.9, 30, 0.7), ManureEvent(1995, 95, 18, 10, 0.9, 30, 0.7),
        ManureEvent(1996, 96, 18, 10, 0.9, 30, 0.7), ManureEvent(1997, 89, 18, 10, 0.9, 30, 0.7),
        ManureEvent(1998, 90, 18, 10, 0.9, 30, 0.7), ManureEvent(1999, 93, 18, 10, 0.9, 30, 0.7)
    ])
])
def test_generate_manure_events(years: List[int], days: List[int], nitrogen: List[float], phosphorus: List[float],
                                coverage: List[float], depth: List[float], surface_frac: List[float], skip: int,
                                repeat: int, expected: List[ManureEvent]) -> None:
    """Tests that a full list of ManureEvents is correctly generated by the ManureSchedule."""
    man_sched = ManureSchedule("test", years, days, nitrogen, phosphorus, coverage, depth, surface_frac, skip, repeat)
    actual = man_sched.generate_manure_events()
    assert actual == expected

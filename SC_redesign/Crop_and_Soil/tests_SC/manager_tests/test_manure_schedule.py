import pytest
from typing import List, Any

from SC_redesign.Crop_and_Soil.manager.manure_schedule import ManureSchedule


@pytest.mark.parametrize("values,expected", [
    ([1, 3, 4], True),
    ([0.0, 1.2, 3.8], True),
    ([], True),
    ([-0.1, 0.1], False),
    ([-2, -4], False)
])
def test_determine_if_all_non_negative_values(values: List[Any], expected: bool) -> None:
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

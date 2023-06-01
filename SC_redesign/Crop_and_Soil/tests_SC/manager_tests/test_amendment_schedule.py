import pytest
from typing import List

from SC_redesign.Crop_and_Soil.manager.amendment_schedule import AmendmentSchedule


@pytest.mark.parametrize("name,years,days,skip,repeat,expected_years,expected_days", [
    ("test_1", 1990, 221, 1, 1, [1990], [221]),
    ("test_2", [1990, 1991, 1993], 180, 2, 3, [1990, 1991, 1993], [180, 180, 180]),
    ("test_3", [1990, 1991], [200, 205], 4, 5, [1990, 1991], [200, 205])
])
def test_init_amendment_schedule(name: str, years: int | List[int], days: int | List[int], skip: int, repeat: int,
                                 expected_years: List[int], expected_days: List[int]) -> None:
    """Tests that base amendment schedules are created correctly."""
    actual = AmendmentSchedule(name, years, days, skip, repeat)
    assert actual.name == name
    assert actual.years == expected_years
    assert actual.days == expected_days
    assert actual.pattern_skip == skip
    assert actual.pattern_repeat == repeat


@pytest.mark.parametrize("years,days,skip,repeat,expected", [
    ([1991, 1993, 1997], [200, 205], 2, 2, "Number of days that event occurs on must be 1 or equal to the number of "
                                           "years the event occurs on."),
    ([1990], [180], -1, 3, "Expected pattern skip to be >= 0, received '-1'."),
    ([1990], [180], 1, -1, "Expected pattern repeat to be >= 0, received '-1'.")
])
def test_init_amendment_schedule_error(years: List[int], days: List[int], skip: int, repeat: int,
                                       expected: str) -> None:
    """Tests that the base amendment schedule throws the correct errors when passed invalid input."""
    with pytest.raises(ValueError) as e:
        AmendmentSchedule("test_error", years, days, skip, repeat)
    assert str(e.value) == expected

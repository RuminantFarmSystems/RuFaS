import pytest
from typing import List

from SC_redesign.Crop_and_Soil.manager.schedule import Schedule


def test_repeat_pattern() -> None:
    """Tests that repeat_pattern correctly repeats patterns."""
    assert Schedule._repeat_pattern([1, 3, 5], 1, 3) == [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23]
    assert Schedule._repeat_pattern([1, 3, 5], 0, 1) == [1, 3, 5, 6, 8, 10]
    assert Schedule._repeat_pattern([2, 3, 7], 3, 2) == [2, 3, 7, 11, 12, 16, 20, 21, 25]
    assert Schedule._repeat_pattern([2, 3, 7], 0, 0) == [2, 3, 7]

    assert Schedule._repeat_pattern([2], 0, 0) == [2]
    assert Schedule._repeat_pattern([2], 3, 1) == [2, 6]
    assert Schedule._repeat_pattern([2], 0, 5) == [2, 3, 4, 5, 6, 7]

    assert Schedule._repeat_pattern([2, 3, 3], 2, 3) == [2, 3, 3, 6, 7, 7, 10, 11, 11, 14, 15, 15]
    assert Schedule._repeat_pattern([1, 1], 0, 4) == [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
    assert Schedule._repeat_pattern([1, 1, 3], 3, 1) == [1, 1, 3, 7, 7, 9]

    assert Schedule._repeat_pattern([], 0, 0) == []
    assert Schedule._repeat_pattern([], 3, 7) == []


@pytest.mark.parametrize("days,expected", [
    ([140, 140, 367], False),
    ([200, 0, 200], False),
    ([100, -30, 100], False),
    ([140, 200, 140], True),
    ([], True)
])
def test_validate_days(days: List[int], expected: bool) -> None:
    """Tests that all days passed to be scheduled are valid."""
    actual = Schedule._validate_days(days)
    assert actual == expected


@pytest.mark.parametrize("years,expected", [
    ([1990, 1989], False),
    ([0, 2], False),
    ([1991, 1991, 1992], True),
    ([1990], True),
    ([], True)
])
def test_validate_years(years: List[int], expected: bool) -> None:
    """Tests that all years passed to be scheduled are valid."""
    actual = Schedule._validate_years(years)
    assert actual == expected


@pytest.mark.parametrize("years,days,skip,repeat,expected", [
    ([1990, 1985], [200], 1, 1, "Years invalid."),
    ([1990], [367], 1, 1, "Days invalid."),
    ([1993], [200, 215], 1, 1, "Number of years and days not equal."),
    ([2000], [200], -1, 1, "Skip invalid."),
    ([1995], [200], 1, -1, "Repeat invalid.")
])
def test_schedule_init_error(years: List[int], days: List[int], skip: int, repeat: int, expected: str) -> None:
    """Tests that Schedule throws the correct error when initialized with invalid parameters."""
    with pytest.raises(ValueError) as e:
        Schedule("test", years, days, skip, repeat)
    assert str(e.value) == expected

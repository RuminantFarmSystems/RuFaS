import pytest
from unittest.mock import MagicMock
from typing import List

from SC_redesign.Crop_and_Soil.manager.events import Event
from RUFAS.classes import Time


@pytest.mark.parametrize("year,day,current_year,current_day,expected", [
    (1, 120, 1, 120, True),
    (2, 200, 2, 201, False),
    (3, 90, 4, 90, False),
    (2, 1, 3, 144, False)
])
def test_occurs_today(year: int, day: int, current_year: int, current_day: int, expected: bool) -> None:
    """Tests that Event objects can correctly determine whether they run on a given day."""
    mocked_time = MagicMock(Time)
    setattr(mocked_time, "year", current_year)
    setattr(mocked_time, "day", current_day)
    event = Event(year, day)

    actual = event.occurs_today(mocked_time)

    assert actual == expected


def test_repeat_pattern() -> None:
    """Tests that repeat_pattern correctly repeats patterns."""
    assert Event.repeat_pattern([1, 3, 5], 1, 3) == [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23]
    assert Event.repeat_pattern([1, 3, 5], 0, 1) == [1, 3, 5, 6, 8, 10]
    assert Event.repeat_pattern([2, 3, 7], 3, 2) == [2, 3, 7, 11, 12, 16, 20, 21, 25]
    assert Event.repeat_pattern([2, 3, 7], 0, 0) == [2, 3, 7]

    assert Event.repeat_pattern([2], 0, 0) == [2]
    assert Event.repeat_pattern([2], 3, 1) == [2, 6]
    assert Event.repeat_pattern([2], 0, 5) == [2, 3, 4, 5, 6, 7]

    assert Event.repeat_pattern([2, 3, 3], 2, 3) == [2, 3, 3, 6, 7, 7, 10, 11, 11, 14, 15, 15]
    assert Event.repeat_pattern([1, 1], 0, 4) == [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
    assert Event.repeat_pattern([1, 1, 3], 3, 1) == [1, 1, 3, 7, 7, 9]

    assert Event.repeat_pattern([], 0, 0) == []
    assert Event.repeat_pattern([], 3, 7) == []


@pytest.mark.parametrize("pattern,skip,repeat,expected", [
    ([2, 1, 5], 0, 0, "Values in pattern cannot be descending, received '[2, 1, 5]'."),
    ([1], -1, 0, "Expected skip to be >= 0, received '-1'."),
    [[1], 0, -1, "Expected repeat to be >= 0, received '-1'."]
])
def test_repeat_pattern_error(pattern: List[int], skip: int, repeat: int, expected: str) -> None:
    """Tests that errors are correctly raised when invalid input is passed."""
    with pytest.raises(ValueError) as e:
        Event.repeat_pattern(pattern, skip, repeat)
    assert str(e.value) == expected

import pytest
from unittest.mock import MagicMock

from SC_redesign.Crop_and_Soil.manager.events import Event


@pytest.mark.parametrize("year,day,current_year,current_day,expected", [
    (1, 120, 1, 120, True),
    (2, 200, 2, 201, False),
    (3, 90, 4, 90, False),
    (2, 1, 3, 144, False)
])
def test_occurs_today(year: int, day: int, current_year: int, current_day: int, expected: bool) -> None:
    """Tests that Event objects can correctly determine whether they run on a given day."""
    mocked_time = MagicMock()
    setattr(mocked_time, "calendar_year", current_year)
    setattr(mocked_time, "day", current_day)
    event = Event(year, day)

    actual = event.occurs_today(mocked_time)

    assert actual == expected


@pytest.mark.parametrize("year1,day1,year2,day2,expected", [
    (1, 240, 1, 240, True),
    (2, 120, 3, 120, False),
    (4, 220, 4, 240, False),
    (5, 150, 6, 200, False)
])
def test_event_equality(year1: int, day1: int, year2: int, day2: int, expected: bool) -> None:
    """Tests that equality is tested correctly between Event objects."""
    event1 = Event(year1, day1)
    event2 = Event(year2, day2)
    actual = event1 == event2
    assert actual == expected

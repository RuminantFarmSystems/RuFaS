import pytest
from typing import List, Any

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


@pytest.mark.parametrize("test_list,length,expected", [
    ([], 3, []),
    ([], 0, []),
    ([1, 2], 1, [1, 2]),
    ([1.0, 2.0], 5, [1.0, 2.0]),
    (["test"], 4, ["test", "test", "test", "test"]),
    ([3], 1, [3]),
    ([5], 5, [5, 5, 5, 5, 5])
])
def test_elongate_list(test_list: List[Any], length: int, expected: List[Any]) -> None:
    """Check that lists are elongated correctly."""
    actual = Schedule._elongate_list(test_list, length)
    assert actual == expected


@pytest.mark.parametrize("years,days,expected", [
    ([1991, 1992, 1992], [140, 140, 367], False),
    ([1990, 1992, 1994], [200, 0, 200], False),
    ([2000, 2002, 2004], [100, -30, 100], False),
    ([2001, 2002, 2003], [140, 200, 140], True),
    ([2000, 2001], [366, 365], True),
    ([2002, 2003], [200, 366], False),
    ([], [], True)
])
def test_validate_days(years: List[int], days: List[int], expected: bool) -> None:
    """Tests that all days passed to be scheduled are valid."""
    actual = Schedule._validate_days(years, days)
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


@pytest.mark.parametrize("name,skip,repeat,expected", [
    ("test_1", -1, 1, "'test_1': expected pattern skip to be >= 0, received '-1'."),
    ("test_2", 1, -1, "'test_2': expected pattern repeat to be >= 0, received '-1'.")
])
def test_validate_pattern_parameters(name: str, skip: int, repeat: int, expected: str) -> None:
    """Tests that errors are correctly raised by Schedule when invalid"""
    with pytest.raises(ValueError) as e:
        test = Schedule(name, [], [], skip, repeat)
        test._validate_pattern_parameters()
    assert str(e.value) == expected

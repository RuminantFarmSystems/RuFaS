from typing import List

import pytest

from RUFAS.routines.field.manager.schedule import Schedule


@pytest.mark.parametrize(
    "years,days,expected",
    [
        ([1991, 1992, 1992], [140, 140, 367], False),
        ([1990, 1992, 1994], [200, 0, 200], False),
        ([2000, 2002, 2004], [100, -30, 100], False),
        ([2001, 2002, 2003], [140, 200, 140], True),
        ([2000, 2001], [366, 365], True),
        ([2002, 2003], [200, 366], False),
        ([], [], True),
    ],
)
def test_validate_days(years: List[int], days: List[int], expected: bool) -> None:
    """Tests that all days passed to be scheduled are valid."""
    actual = Schedule._validate_days(years, days)
    assert actual == expected


@pytest.mark.parametrize(
    "years,expected",
    [
        ([1990, 1989], False),
        ([0, 2], False),
        ([1991, 1991, 1992], True),
        ([1990], True),
        ([], True),
    ],
)
def test_validate_years(years: List[int], expected: bool) -> None:
    """Tests that all years passed to be scheduled are valid."""
    actual = Schedule._validate_years(years)
    assert actual == expected


@pytest.mark.parametrize(
    "name,skip,repeat,expected",
    [
        ("test_1", -1, 1, "'test_1': expected pattern skip to be >= 0, received '-1'."),
        (
            "test_2",
            1,
            -1,
            "'test_2': expected pattern repeat to be >= 0, received '-1'.",
        ),
    ],
)
def test_validate_pattern_parameters(name: str, skip: int, repeat: int, expected: str) -> None:
    """Tests that errors are correctly raised by Schedule when invalid"""
    with pytest.raises(ValueError) as e:
        test = Schedule(name, [], [], skip, repeat)
        test._validate_pattern_parameters()
    assert str(e.value) == expected

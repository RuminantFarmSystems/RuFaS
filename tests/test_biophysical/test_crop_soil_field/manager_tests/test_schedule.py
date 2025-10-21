from typing import List

import pytest

from RUFAS.biophysical.field.manager.schedule import Schedule


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


def test_validate_equal_lengths_valid() -> None:
    """Test that the validation for valid parameter length are valid."""
    assert Schedule.validate_equal_lengths(
        "valid tests", year=[2023, 2024, 2025], day=[1, 3, 64], depth=[1.1, 1.2, 5.2]
    )


def test_validate_equal_lengths_invalid() -> None:
    """Test that the validation for invalid parameter length are valid."""
    try:
        Schedule.validate_equal_lengths("invalid tests", year=[2023, 2024, 2025], day=[1, 3, 64], depth=[1.1, 1.2])
        assert False
    except ValueError as e:
        assert e.args[0] == (
            "invalid tests Mismatch in length of parameters. Provided parameters are: year=[2023, "
            "2024, 2025], day=[1, 3, 64], depth=[1.1, 1.2]. Lengths are: {'year': 3, 'day': 3, "
            "'depth': 2}."
        )


@pytest.mark.parametrize(
    "pattern, skip, repeat, expected",
    [
        (
            [1, 3, 5],
            1,
            3,
            [
                1,
                3,
                5,
                7,
                9,
                11,
                13,
                15,
                17,
                19,
                21,
                23,
            ],
        ),
        ([1, 3, 5], 0, 1, [1, 3, 5, 6, 8, 10]),
        (
            [2, 3, 7],
            3,
            2,
            [
                2,
                3,
                7,
                11,
                12,
                16,
                20,
                21,
                25,
            ],
        ),
        ([2, 3, 7], 0, 0, [2, 3, 7]),
        ([2], 0, 0, [2]),
        ([2], 3, 1, [2, 6]),
        ([2], 0, 5, [2, 3, 4, 5, 6, 7]),
        (
            [2, 3, 3],
            2,
            3,
            [
                2,
                3,
                3,
                6,
                7,
                7,
                10,
                11,
                11,
                14,
                15,
                15,
            ],
        ),
        ([1, 1], 0, 4, [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]),
        ([1, 1, 3], 3, 1, [1, 1, 3, 7, 7, 9]),
        ([], 0, 0, []),
        ([], 3, 7, []),
    ],
)
def test_repeat_pattern(pattern: List[int], skip: int, repeat: int, expected: list) -> None:
    """Tests that repeat_pattern correctly repeats patterns."""
    assert Schedule.repeat_pattern(pattern, skip, repeat) == expected


def test_prepare_events() -> None:
    """Test prepare_events to ensure correct event arguments preparation."""
    years = [2022, 2023]
    days = [100, 200]
    additional_attributes_events = [[1, 2], [3, 4]]
    pattern_skip = 0
    pattern_repeat = 1
    schedule = Schedule("test", [1], [1])

    result = schedule.prepare_events(years, days, additional_attributes_events, pattern_skip, pattern_repeat)

    assert result == [
        (1, 3, 2022, 100),
        (2, 4, 2023, 200),
        (1, 3, 2024, 100),
        (2, 4, 2025, 200),
    ]

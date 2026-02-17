import datetime
import math
import re
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import pytest
from matplotlib.dates import DateFormatter, date2num
from pytest import approx, raises
from pytest_mock.plugin import MockerFixture

from RUFAS.util import Utility, Aggregator


def test_calc_average() -> None:
    """Unit test for function calc_average in file util.py"""
    # Normal case
    result = Utility.calc_average(num_values=9, cur_avg=5, new_value=6)
    actual_new_num_values, actual_new_avg = result
    assert actual_new_num_values == 10
    assert actual_new_avg == approx(5.1)  # (9 * 5 + 6) / 10

    # Given a count of 0 and an average value of 0.0,
    # the function should return whatever the new value is.
    result = Utility.calc_average(num_values=0, cur_avg=0.0, new_value=6.0)
    actual_new_num_values, actual_new_avg = result
    assert actual_new_num_values == 1
    assert actual_new_avg == approx(6.0)


def test_remove_items_from_list_by_indices() -> None:
    """Unit test for function remove_items_from_list_by_indices in file util.py"""
    # Given an empty list and an empty list of removal indices,
    # the function should do nothing.
    arr: list[Any] = []
    del_idx: list[int] = []
    Utility.remove_items_from_list_by_indices(arr, del_idx)
    assert len(arr) == 0

    # Given a non-empty list and an empty list of removal indices,
    # the function should do nothing.
    arr = [0, 1, 2]
    del_idx = []
    Utility.remove_items_from_list_by_indices(arr, del_idx)
    assert arr == [0, 1, 2]

    # Given a list of size 1 and the removal index of 0,
    # the function should return an empty list.
    arr = [0]
    del_idx = [0]
    Utility.remove_items_from_list_by_indices(arr, del_idx)
    assert len(arr) == 0

    # Given a list of size 2 and one valid removal index,
    # the function should return a correct list of size 1.
    arr = [10, 20]
    del_idx = [0]
    Utility.remove_items_from_list_by_indices(arr, del_idx)
    assert arr == [20]

    arr = [10, 20]
    del_idx = [1]
    Utility.remove_items_from_list_by_indices(arr, del_idx)
    assert arr == [10]

    # Given a list of size 3 and a list of 2 removal indices,
    # the function should return a correct list of size 1.
    arr = [10, 20, 30]
    del_idx = [0, 1]
    Utility.remove_items_from_list_by_indices(arr, del_idx)
    assert arr == [30]

    arr = [10, 20, 30]
    del_idx = [1, 2]
    Utility.remove_items_from_list_by_indices(arr, del_idx)
    assert arr == [10]

    arr = [10, 20, 30]
    del_idx = [0, 2]
    Utility.remove_items_from_list_by_indices(arr, del_idx)
    assert arr == [20]

    # Given an empty list and a non-empty list of removal indices,
    # the function should raise IndexError.
    arr = []
    del_idx = [0]
    with raises(IndexError):
        Utility.remove_items_from_list_by_indices(arr, del_idx)


def test_percent_calculator() -> None:
    """Unit test for function percent_calculator in file util.py"""
    # Normal case
    # Given any random non-zero denominator,
    # the function should return correct percentages.
    pc = Utility.percent_calculator(denominator=20)
    assert pc(0) == approx(0.0)
    assert pc(20) == approx(100.0)
    assert pc(8) == approx(40.0)  # e.g., 8/20 = 40%
    assert pc(-8) == approx(-40.0)
    assert pc(24) == approx(120.0)

    # Given a denominator of 100,
    # the function should return the numerator as percentage.
    pc = Utility.percent_calculator(denominator=100)
    assert pc(0.0) == approx(0.0)
    assert pc(12.3) == approx(12.3)
    assert pc(100.0) == approx(100.0)

    # Given a 0 denominator, the function should raise a ZeroDivisionError.
    pc = Utility.percent_calculator(denominator=0)
    with raises(ZeroDivisionError):
        pc(1.0)


def test_convert_list_of_dicts_to_dict_of_lists_empty_list() -> None:
    result = Utility.convert_list_of_dicts_to_dict_of_lists([])
    assert result == {}


def test_convert_list_of_dicts_to_dict_of_lists_single_dict() -> None:
    input_data = [{"a": 1, "b": 2}]
    expected_result = {"a": [1], "b": [2]}
    result = Utility.convert_list_of_dicts_to_dict_of_lists(input_data)
    assert result == expected_result


def test_convert_list_of_dicts_to_dict_of_lists_multiple_dicts() -> None:
    input_data = [{"a": 1, "b": 2}, {"a": 3, "c": 4}]
    expected_result = {"a": [1, 3], "b": [2], "c": [4]}
    result = Utility.convert_list_of_dicts_to_dict_of_lists(input_data)
    assert result == expected_result


def test_convert_list_of_dicts_to_dict_of_lists_empty_values() -> None:
    input_data: list[dict[str, Any]] = [{"a": 1, "b": 2}, {"a": None, "b": 3}]
    expected_result = {"a": [1, None], "b": [2, 3]}
    result = Utility.convert_list_of_dicts_to_dict_of_lists(input_data)
    assert result == expected_result


def test_convert_list_of_dicts_to_dict_of_lists_empty_keys() -> None:
    input_data = [{"a": 1, "b": 2}, {"": 3, "b": 4}]
    expected_result = {"a": [1], "b": [2, 4], "": [3]}
    result = Utility.convert_list_of_dicts_to_dict_of_lists(input_data)
    assert result == expected_result


def test_get_timestamp() -> None:
    """Unit test for the function get_timestamp in file util.py"""

    # Arrange
    timestamp_with_millis_pattern = r"\d{2}-[A-Za-z]{3}-\d{4}_[A-Za-z]{3}_\d{2}-\d{2}-\d{2}\.\d{6}"
    timestamp_without_millis_pattern = r"\d{2}-[A-Za-z]{3}-\d{4}_[A-Za-z]{3}_\d{2}-\d{2}-\d{2}"

    # Act & Assert
    assert re.match(timestamp_with_millis_pattern, Utility.get_timestamp(include_millis=True))
    assert re.match(timestamp_without_millis_pattern, Utility.get_timestamp(include_millis=False))


@pytest.mark.parametrize(
    "dict_to_be_filtered, filter_patterns, filter_by_exclusion, expected_result",
    [
        (
            {"var1": 1, "var2": 2, "var3": 3},
            ["var1", "var2"],
            False,
            {"var1": 1, "var2": 2},
        ),
        ({"var1": 1, "var2": 2, "var3": 3}, ["var1", "var2"], True, {"var3": 3}),
        ({"var1": 1, "var2": 2, "var3": 3}, ["var4"], False, {}),
        (
            {"var1": 1, "var2": 2, "var3": 3},
            ["var4"],
            True,
            {"var1": 1, "var2": 2, "var3": 3},
        ),
        ({}, ["var1"], False, {}),
        ({"var1": 1, "var2": 2, "var3": 3}, [], False, {}),
    ],
)
def test_filter_dictionary(
    dict_to_be_filtered: Dict[str, Any],
    filter_patterns: List[str],
    filter_by_exclusion: bool,
    expected_result: Dict[str, Any],
) -> None:
    assert Utility.filter_dictionary(dict_to_be_filtered, filter_patterns, filter_by_exclusion) == expected_result


@pytest.mark.parametrize(
    "date,start,end,expected",
    [
        (datetime.date(2024, 6, 1), 0, 0, [datetime.date(2024, 6, 1)]),
        (datetime.date(2024, 6, 1), 2, 2, [datetime.date(2024, 6, 3)]),
        (
            datetime.date(2024, 6, 1),
            2,
            4,
            [datetime.date(2024, 6, 3), datetime.date(2024, 6, 4), datetime.date(2024, 6, 5)],
        ),
        (
            datetime.date(2023, 12, 31),
            -1,
            1,
            [datetime.date(2023, 12, 30), datetime.date(2023, 12, 31), datetime.date(2024, 1, 1)],
        ),
        (
            datetime.date(2024, 1, 1),
            -5,
            -3,
            [datetime.date(2023, 12, 27), datetime.date(2023, 12, 28), datetime.date(2023, 12, 29)],
        ),
        (
            datetime.date(2024, 3, 1),
            -2,
            0,
            [datetime.date(2024, 2, 28), datetime.date(2024, 2, 29), datetime.date(2024, 3, 1)],
        ),
        (
            datetime.date(2024, 2, 28),
            0,
            2,
            [datetime.date(2024, 2, 28), datetime.date(2024, 2, 29), datetime.date(2024, 3, 1)],
        ),
        (
            datetime.date(2023, 2, 28),
            0,
            2,
            [datetime.date(2023, 2, 28), datetime.date(2023, 3, 1), datetime.date(2023, 3, 2)],
        ),
    ],
)
def test_generate_time_series(date: datetime.date, start: int, end: int, expected: list[datetime.date]) -> None:
    """Tests that time series are correctly generated by generate_time_series."""
    actual = Utility.generate_time_series(date, start, end)

    assert actual == expected


def test_generate_time_series_error() -> None:
    """Tests that generate_time_series correctly throws error when given invalid input."""
    with pytest.raises(ValueError, match="greater than ending offset"):
        Utility.generate_time_series(datetime.date(2024, 6, 1), 2, 1)


@pytest.mark.parametrize("celsius, expected", [(0.0, 273.15), (-273.15, 0.0), (20.0, 293.15)])
def test_convert_celsius_to_kelvin(celsius: float, expected: float) -> None:
    """Test that degrees Celsius is converted to degrees Kelvin correctly."""
    actual = Utility.convert_celsius_to_kelvin(celsius)

    assert actual == expected


@pytest.mark.parametrize(
    "year,day,expected",
    [
        (2020, 1, datetime.date(2020, 1, 1)),
        (2020, 60, datetime.date(2020, 2, 29)),
        (2021, 60, datetime.date(2021, 3, 1)),
        (2020, 365, datetime.date(2020, 12, 30)),
        (2020, 366, datetime.date(2020, 12, 31)),
        (2021, 365, datetime.date(2021, 12, 31)),
    ],
)
def test_convert_ordinal_date_to_month_date(year: int, day: int, expected: datetime.date) -> None:
    """Tests that convert_ordinal_date_to_month_date correctly converts dates."""
    actual = Utility.convert_ordinal_date_to_month_date(year, day)

    assert actual == expected


@pytest.mark.parametrize("year,day", [(2020, 0), (2020, 367), (2021, 366)])
def test_convert_ordinal_date_to_month_date_error(year: int, day: int) -> None:
    """Tests that convert_ordinal_date_to_month_date throws an error when given invalid date."""
    with pytest.raises(ValueError, match="Invalid day"):
        Utility.convert_ordinal_date_to_month_date(year, day)


def test_remove_special_chars() -> None:
    """Tests remove_special_chars() function in util.py"""
    charred_word = '<>:/w"o|\\r?d?*.'
    expected_result = "word"
    assert Utility.remove_special_chars(charred_word) == expected_result


@pytest.mark.parametrize(
    "dict_of_lists, expected",
    [
        (
            {"a": [1, 2, 3], "b": [4, 5, 6], "c": [7, 8, 9]},
            [{"a": 1, "b": 4, "c": 7}, {"a": 2, "b": 5, "c": 8}, {"a": 3, "b": 6, "c": 9}],
        )
    ],
)
def test_convert_dict_of_lists_to_list_of_dicts(
    dict_of_lists: dict[str, list[Any]], expected: list[dict[str, Any]]
) -> None:
    """Test that dictionaries of lists are converted to a list of dictionaries correctly."""
    actual = Utility.convert_dict_of_lists_to_list_of_dicts(dict_of_lists)

    assert actual == expected


def test_flatten_keys_to_nested_structure_nested_dict() -> None:
    x = {"a.i.c": 1, "a.i.d": 2, "a.j.c": 3, "a.j.d": 4, "b.i.c": 5, "b.i.d": 6, "b.j.c": 7, "b.j.d": 8}
    actual = Utility.flatten_keys_to_nested_structure(x)
    expected = {
        "a": {"i": {"c": 1, "d": 2}, "j": {"c": 3, "d": 4}},
        "b": {"i": {"c": 5, "d": 6}, "j": {"c": 7, "d": 8}},
    }
    assert actual == expected


def test_flatten_keys_to_nested_structure_flat_dict() -> None:
    x = {"aic": 1, "aid": 2, "ajc": 3, "ajd": 4, "bic": 5, "bid": 6, "bjc": 7, "bjd": 8}
    actual = Utility.flatten_keys_to_nested_structure(x)
    assert actual == x


def test_flatten_keys_to_nested_structure_dict_w_list() -> None:
    x = {
        "a.i.0": 1,
        "a.i.1": 2,
        "a.j.c": 3,
        "a.j.d": 4,
        "b.i.c": 5,
        "b.i.d": 6,
        "b.j.c": 7,
        "b.j.d.0": 8,
        "b.j.d.1.x.0": 9,
        "b.j.d.1.x.1": 10,
        "b.j.d.1.y": 11,
        "b.j.d.2": 12,
    }
    actual = Utility.flatten_keys_to_nested_structure(x)
    expected = {
        "a": {"i": [1, 2], "j": {"c": 3, "d": 4}},
        "b": {"i": {"c": 5, "d": 6}, "j": {"c": 7, "d": [8, {"x": [9, 10], "y": 11}, 12]}},
    }
    assert actual == expected


@pytest.mark.parametrize(
    "data_to_pad,fill_value,gap_pad,end_pad,expected",
    [
        (
            {
                "a": {
                    "values": ["a", "b", "c"],
                    "info_maps": [
                        {"simulation_day": 1, "units": "kg"},
                        {"simulation_day": 4, "units": "kg"},
                        {"simulation_day": 5, "units": "kg"},
                    ],
                },
                "b": {
                    "values": ["d", "e", "f"],
                    "info_maps": [
                        {"simulation_day": 3, "units": "g"},
                        {"simulation_day": 4, "units": "g"},
                        {"simulation_day": 6, "units": "g"},
                    ],
                },
            },
            math.nan,
            False,
            True,
            {
                "a": {
                    "values": ["a", "a", "a", "b", "c", math.nan],
                    "info_maps": [
                        {"simulation_day": 1, "units": "kg"},
                        {"simulation_day": 2, "units": "kg"},
                        {"simulation_day": 3, "units": "kg"},
                        {"simulation_day": 4, "units": "kg"},
                        {"simulation_day": 5, "units": "kg"},
                        {"simulation_day": 6, "units": "kg"},
                    ],
                },
                "b": {
                    "values": [math.nan, math.nan, "d", "e", "e", "f"],
                    "info_maps": [
                        {"simulation_day": 1, "units": "g"},
                        {"simulation_day": 2, "units": "g"},
                        {"simulation_day": 3, "units": "g"},
                        {"simulation_day": 4, "units": "g"},
                        {"simulation_day": 5, "units": "g"},
                        {"simulation_day": 6, "units": "g"},
                    ],
                },
            },
        ),
        (
            {
                "a": {
                    "values": ["a", "b", "c"],
                    "info_maps": [
                        {"simulation_day": 1, "units": "kg"},
                        {"simulation_day": 4, "units": "kg"},
                        {"simulation_day": 5, "units": "kg"},
                    ],
                },
                "b": {
                    "values": ["d", "e", "f"],
                    "info_maps": [
                        {"simulation_day": 3, "units": "g"},
                        {"simulation_day": 4, "units": "g"},
                        {"simulation_day": 6, "units": "g"},
                    ],
                },
            },
            math.nan,
            True,
            False,
            {
                "a": {
                    "values": ["a", math.nan, math.nan, "b", "c", "c"],
                    "info_maps": [
                        {"simulation_day": 1, "units": "kg"},
                        {"simulation_day": 2, "units": "kg"},
                        {"simulation_day": 3, "units": "kg"},
                        {"simulation_day": 4, "units": "kg"},
                        {"simulation_day": 5, "units": "kg"},
                        {"simulation_day": 6, "units": "kg"},
                    ],
                },
                "b": {
                    "values": [math.nan, math.nan, "d", "e", math.nan, "f"],
                    "info_maps": [
                        {"simulation_day": 1, "units": "g"},
                        {"simulation_day": 2, "units": "g"},
                        {"simulation_day": 3, "units": "g"},
                        {"simulation_day": 4, "units": "g"},
                        {"simulation_day": 5, "units": "g"},
                        {"simulation_day": 6, "units": "g"},
                    ],
                },
            },
        ),
        (
            {
                "a": {"values": ["a"], "info_maps": [{"simulation_day": 2, "units": "pi"}]},
                "b": {
                    "values": ["b", "c"],
                    "info_maps": [{"simulation_day": 3, "units": "pi"}, {"simulation_day": 4, "units": "pi"}],
                },
            },
            None,
            True,
            False,
            {
                "a": {
                    "values": ["a", "a", "a"],
                    "info_maps": [
                        {"simulation_day": 2, "units": "pi"},
                        {"simulation_day": 3, "units": "pi"},
                        {"simulation_day": 4, "units": "pi"},
                    ],
                },
                "b": {
                    "values": [None, "b", "c"],
                    "info_maps": [
                        {"simulation_day": 2, "units": "pi"},
                        {"simulation_day": 3, "units": "pi"},
                        {"simulation_day": 4, "units": "pi"},
                    ],
                },
            },
        ),
        (
            {
                "a": {
                    "values": ["a", "b"],
                    "info_maps": [{"simulation_day": 1, "units": "ha"}, {"simulation_day": 2, "units": "ha"}],
                },
                "b": {
                    "values": ["c", "d"],
                    "info_maps": [{"simulation_day": 1, "units": "ha"}, {"simulation_day": 2, "units": "ha"}],
                },
            },
            8,
            False,
            True,
            {
                "a": {
                    "values": ["a", "b"],
                    "info_maps": [{"simulation_day": 1, "units": "ha"}, {"simulation_day": 2, "units": "ha"}],
                },
                "b": {
                    "values": ["c", "d"],
                    "info_maps": [{"simulation_day": 1, "units": "ha"}, {"simulation_day": 2, "units": "ha"}],
                },
            },
        ),
        (
            {
                "a": {
                    "values": ["a", "b"],
                    "info_maps": [{"simulation_day": 1, "units": "ha^2"}, {"simulation_day": 3, "units": "ha^2"}],
                },
                "b": {
                    "values": ["c", "d"],
                    "info_maps": [{"simulation_day": 1, "units": "l"}, {"simulation_day": 3, "units": "l"}],
                },
            },
            "fill",
            True,
            False,
            {
                "a": {
                    "values": ["a", "fill", "b"],
                    "info_maps": [
                        {"simulation_day": 1, "units": "ha^2"},
                        {"simulation_day": 2, "units": "ha^2"},
                        {"simulation_day": 3, "units": "ha^2"},
                    ],
                },
                "b": {
                    "values": ["c", "fill", "d"],
                    "info_maps": [
                        {"simulation_day": 1, "units": "l"},
                        {"simulation_day": 2, "units": "l"},
                        {"simulation_day": 3, "units": "l"},
                    ],
                },
            },
        ),
        (
            {
                "a": {
                    "values": ["a", "b"],
                    "info_maps": [{"simulation_day": 1, "units": "GB"}, {"simulation_day": 3, "units": "GB"}],
                },
            },
            math.pi,
            True,
            True,
            {
                "a": {
                    "values": ["a", math.pi, "b"],
                    "info_maps": [
                        {"simulation_day": 1, "units": "GB"},
                        {"simulation_day": 2, "units": "GB"},
                        {"simulation_day": 3, "units": "GB"},
                    ],
                }
            },
        ),
    ],
)
def test_expand_data_temporally(
    data_to_pad: dict[str, dict[str, list[Any]]],
    fill_value: Any,
    gap_pad: bool,
    end_pad: bool,
    expected: dict[str, dict[str, list[Any]]],
) -> None:
    """Tests the utility method expand_data_temporally."""
    actual = Utility.expand_data_temporally(
        data_to_pad, fill_value=fill_value, use_fill_value_in_gaps=gap_pad, use_fill_value_at_end=end_pad
    )

    assert actual == expected


def test_expand_data_temporally_errors() -> None:
    """Tests that errors are correctly raised by expand_data_temporally."""
    empty_data: dict[str, dict[str, list[Any]]] = {}
    with pytest.raises(ValueError, match="empty dataset"):
        Utility.expand_data_temporally(empty_data)

    data_one = {"a": {"values": ["a", "b"]}, "b": {"values": ["c", "d"]}}
    with pytest.raises(TypeError, match="no info maps"):
        Utility.expand_data_temporally(data_one)

    data_two: dict[str, dict[str, list[Any]]] = {
        "a": {"values": ["a", "b"], "info_maps": [{"simulation_day": 1}]},
        "b": {"values": ["c", "d"], "info_maps": [{"simulation_day": 1}, {"simulation_day": 3}]},
    }
    with pytest.raises(ValueError, match="number of values and info maps"):
        Utility.expand_data_temporally(data_two)

    data_three: dict[str, dict[str, list[Any]]] = {
        "a": {"values": ["a", "b"], "info_maps": [{"simulation_day": 1}, {"foo": "bar"}]},
        "b": {"values": ["c", "d"], "info_maps": [{"simulation_day": 1}, {"simulation_day": 3}]},
    }
    with pytest.raises(ValueError, match="simulation day value in every info map"):
        Utility.expand_data_temporally(data_three)


def test_deep_merge_dict() -> None:
    x = {
        "a": {"i": {"c": 1, "d": 2}, "j": {"c": 3, "d": 4}},
        "b": {"i": {"c": 5, "d": 6}, "j": {"c": 7, "d": 8}},
    }

    y = {
        "b": {"j": {"d": 9, "e": 10}, "k": 11},
    }

    expected = {
        "a": {"i": {"c": 1, "d": 2}, "j": {"c": 3, "d": 4}},
        "b": {"i": {"c": 5, "d": 6}, "j": {"c": 7, "d": 9, "e": 10}, "k": 11},
    }
    Utility.deep_merge(x, y)
    assert x == expected


def test_deep_merge_dict_w_list() -> None:
    a = {
        "a": {"i": [1, 2], "j": {"c": 3, "d": 4}},
        "b": {"i": {"c": 5, "d": 6}, "j": {"c": 7, "d": [8, {"x": [9, 10], "y": 11}, 12]}},
    }

    b = {
        "a": {"i": [11, 12, 13]},
        "b": {"i": {"c": 15}, "j": {"d": [8, {"x": [19, 110]}]}},
    }

    expected = {
        "a": {"i": [11, 12, 13], "j": {"c": 3, "d": 4}},
        "b": {"i": {"c": 15, "d": 6}, "j": {"c": 7, "d": [8, {"x": [19, 110], "y": 11}, 12]}},
    }
    Utility.deep_merge(a, b)
    assert a == expected


class DummyClass:
    def __init__(self, value: int) -> None:
        self.value = value


class DummyNestedClass:
    def __init__(self, value: int) -> None:
        self.value = DummyClass(value)


@pytest.mark.parametrize(
    "input_obj, depth, max_depth, expected_output",
    [
        (42, 0, 1, 42),
        (3.14, 0, 1, 3.14),
        ("test", 0, 1, "test"),
        (True, 0, 1, True),
        (False, 0, 1, False),
        (None, 0, 1, None),
        ([], 0, 1, []),
        ((), 0, 1, ()),
        ({}, 0, 1, {}),
        (set(), 0, 1, []),
        ([1, "test", True], 0, 1, [1, "test", True]),
        ((1, "test", True), 0, 1, (1, "test", True)),
        ({1, 2, 3}, 0, 1, [1, 2, 3]),
        ({"a": 1, "b": 2}, 0, 1, {"a": 1, "b": 2}),
        ({"a": [1, 2, 3], "b": {"c": 4}}, 0, 3, {"a": [1, 2, 3], "b": {"c": 4}}),
        (["a", (1, 2), {"b": 3}], 0, 2, ["a", (1, 2), {"b": 3}]),
        ([1, [2, [3, 4], 5], 6], 0, 2, [1, [2, "[3, 4]", 5], 6]),
        ({"a": {"b": {"c": 42}}}, 0, 2, {"a": {"b": {"c": 42}}}),
        (DummyClass(42), 0, 1, {"value": 42}),
        (DummyNestedClass(42), 0, 2, {"value": {"value": 42}}),
        ({"a": {"b": DummyClass(42)}}, 0, 3, {"a": {"b": {"value": 42}}}),
        (
            [42, "test", 3.14, True, None, [1, 2, 3], {"a": 1}],
            0,
            2,
            [42, "test", 3.14, True, None, [1, 2, 3], {"a": 1}],
        ),
    ],
)
def test_make_serializable_recursive(
    input_obj: object,
    depth: int,
    max_depth: int,
    expected_output: object,
    mocker: MockerFixture,
) -> None:
    """Unit test for function _make_serializable() in file util.py"""
    # Arrange
    _ = mocker.patch.object(Utility, "_get_str", side_effect=lambda x: str(x))

    # Act
    result = Utility._make_serializable(input_obj, depth, max_depth)

    # Assert
    assert result == expected_output


@pytest.mark.parametrize("mean,std_dev", [(20.0, 1.0), (0.0, 0.0)])
def test_generate_random_number(mocker: MockerFixture, mean: float, std_dev: float) -> None:
    """Tests that random numbers are generated properly."""
    random = mocker.patch("RUFAS.util.np.random.normal", return_value=10.0)

    actual = Utility.generate_random_number(mean, std_dev)

    assert actual == 10.0
    random.assert_called_once_with(mean, std_dev)


@pytest.mark.parametrize(
    "input_dictionary, expected_output",
    [
        ({"a": 1, "b": {"c": 2, "d": 3}}, {"a": 1, "b.c": 2, "b.d": 3}),
        ({"x": {"y": {"z": 4}}}, {"x.y.z": 4}),
        (
            {
                "name": "John",
                "contacts": [
                    {"type": "email", "value": "john@example.com"},
                    {"type": "phone", "value": "123-456-7890"},
                ],
            },
            {
                "name": "John",
                "contacts_0.type": "email",
                "contacts_0.value": "john@example.com",
                "contacts_1.type": "phone",
                "contacts_1.value": "123-456-7890",
            },
        ),
        (
            {"user": {"id": 1, "name": "Alice", "attributes": {"age": 30, "languages": ["English", "Spanish"]}}},
            {
                "user.id": 1,
                "user.name": "Alice",
                "user.attributes.age": 30,
                "user.attributes.languages": ["English", "Spanish"],
            },
        ),
        ({}, {}),
        (
            {"empty_dict": {}, "empty_list": [], "valid_key": "value"},
            {"empty_dict": {}, "empty_list": [], "valid_key": "value"},
        ),
        ({"items": [{}]}, {}),
    ],
)
def test_flatten_dictionary(input_dictionary: dict[str, Any], expected_output: dict[str, Any]) -> None:
    """Tests the flatten_dictionary() in Utility"""
    actual_output = Utility.flatten_dictionary(input_dictionary)
    assert actual_output == expected_output


@pytest.mark.parametrize(
    "saved_csv_contents, saved_csv_files, import_previous_csv_content, expected_result",
    [
        (
            [
                pd.DataFrame(
                    {
                        "property_group": ["group1", "group1"],
                        "variable_name": ["var1", "var2"],
                        "value": [1, 2],
                    }
                )
            ],
            ["file1.csv"],
            None,
            pd.DataFrame(
                {
                    "property_group": ["group1", "group1"],
                    "variable_name": ["var1", "var2"],
                    "value": [1, 2],
                }
            ),
        ),
        (
            [
                pd.DataFrame(
                    {
                        "property_group": ["group1", "group1"],
                        "variable_name": ["var1", "var2"],
                        "value": [1, 2],
                    }
                )
            ],
            ["file1.csv"],
            pd.DataFrame(
                {
                    "property_group": ["group1", "group3"],
                    "variable_name": ["var1", "var4"],
                    "value": [100, 400],
                }
            ),
            pd.DataFrame(
                {
                    "property_group": ["group1", "group1", "group3"],
                    "variable_name": ["var1", "var2", "var4"],
                    "value_1": [100, np.nan, 400],
                    "value_2": [1, 2, np.nan],
                }
            ),
        ),
        (
            [
                pd.DataFrame(
                    {
                        "property_group": ["group1", "group1"],
                        "variable_name": ["var1", "var2"],
                        "value": [1, 2],
                    }
                ),
                pd.DataFrame(
                    {
                        "property_group": ["group1", "group2"],
                        "variable_name": ["var1", "var3"],
                        "value": [10, 30],
                    }
                ),
            ],
            ["file1.csv", "file2.csv"],
            None,
            pd.DataFrame(
                {
                    "property_group": ["group1", "group1", "group2"],
                    "variable_name": ["var1", "var2", "var3"],
                    "value_1": [1, 2, np.nan],
                    "value_2": [10, np.nan, 30],
                }
            ),
        ),
        (
            [
                pd.DataFrame(
                    {
                        "property_group": ["group1", "group1"],
                        "variable_name": ["var1", "var2"],
                        "value": [1, 2],
                    }
                ),
                pd.DataFrame(
                    {
                        "property_group": ["group1", "group2"],
                        "variable_name": ["var1", "var3"],
                        "value": [10, 30],
                    }
                ),
            ],
            ["file1.csv", "file2.csv"],
            pd.DataFrame(
                {
                    "property_group": ["group1", "group1", "group3"],
                    "variable_name": ["var1", "var2", "var4"],
                    "value_1": [100, np.nan, 400],
                    "value_2": [1, 2, np.nan],
                }
            ),
            pd.DataFrame(
                {
                    "property_group": ["group1", "group1", "group2"],
                    "variable_name": ["var1", "var2", "var3"],
                    "value_1": [1, 2, np.nan],
                    "value_2": [10, np.nan, 30],
                    "value_3": [1, 2, np.nan],
                    "value_4": [10, np.nan, 30],
                }
            ),
        ),
    ],
)
def test_combine(
    saved_csv_contents: list[pd.DataFrame],
    saved_csv_files: list[str],
    import_previous_csv_content: pd.DataFrame,
    expected_result: pd.DataFrame,
    mocker: MockerFixture,
) -> None:
    read_csv_return = saved_csv_contents.copy()
    if import_previous_csv_content is not None:
        read_csv_return = [import_previous_csv_content] + read_csv_return
    mock_read_csv = mocker.patch("pandas.read_csv", side_effect=read_csv_return)

    mock_to_csv = mocker.patch("pandas.DataFrame.to_csv")

    mock_list_dir = mocker.patch("os.listdir", return_value=saved_csv_files)
    mock_rmtree = mocker.patch("shutil.rmtree")

    saved_csv_working_folder = Path("dummy/working/folder")
    output_csv_path = Path("dummy/output/folder")
    import_csv_path = Path("dummy/import/folder") if import_previous_csv_content is not None else Path("")

    Utility.combine_saved_input_csv(saved_csv_working_folder, output_csv_path, import_csv_path)

    assert mock_read_csv.call_count == len(read_csv_return)

    mock_to_csv.assert_called_once()
    mock_list_dir.assert_called_once_with(saved_csv_working_folder)

    mock_rmtree.assert_called_once_with(saved_csv_working_folder)


def test_convert_dict_of_lists_to_list_of_dicts_normal_case() -> None:
    input_dict = {"id": [1, 2, 3], "name": ["Alice", "Bob", "Charlie"], "age": [25, 30, 35]}
    expected_output = [
        {"id": 1, "name": "Alice", "age": 25},
        {"id": 2, "name": "Bob", "age": 30},
        {"id": 3, "name": "Charlie", "age": 35},
    ]
    assert Utility.convert_dict_of_lists_to_list_of_dicts(input_dict) == expected_output


def test_convert_dict_of_lists_to_list_of_dicts_empty_input() -> None:
    input_dict = {}
    expected_output = []
    assert Utility.convert_dict_of_lists_to_list_of_dicts(input_dict) == expected_output


def test_convert_dict_of_lists_to_list_of_dicts_single_element_lists() -> None:
    input_dict = {"id": [1], "name": ["Alice"], "age": [25]}
    expected_output = [{"id": 1, "name": "Alice", "age": 25}]
    assert Utility.convert_dict_of_lists_to_list_of_dicts(input_dict) == expected_output


def test_convert_list_to_dict_by_key_basic() -> None:
    list_of_dicts = [
        {"ID": 1, "value": 2, "other_keys": "other values"},
        {"ID": 3, "value": 4, "other_keys": "other values"},
    ]
    expected_output = {1: {"value": 2, "other_keys": "other values"}, 3: {"value": 4, "other_keys": "other values"}}
    assert Utility.convert_list_to_dict_by_key(list_of_dicts, "ID") == expected_output


def test_convert_list_to_dict_by_key_empty_list() -> None:
    list_of_dicts = []
    expected_output = {}
    assert Utility.convert_list_to_dict_by_key(list_of_dicts, "ID") == expected_output


def test_convert_list_to_dict_by_key_missing_key() -> None:
    list_of_dicts = [{"ID": 1, "value": 2}, {"value": 3}]  # Missing 'ID'
    with pytest.raises(KeyError):
        Utility.convert_list_to_dict_by_key(list_of_dicts, "ID")


def test_convert_list_to_dict_by_key_different_key() -> None:
    list_of_dicts = [{"unique_id": 1, "value": "A"}, {"unique_id": 2, "value": "B"}]
    expected_output = {1: {"value": "A"}, 2: {"value": "B"}}
    assert Utility.convert_list_to_dict_by_key(list_of_dicts, "unique_id") == expected_output


def test_find_max_index_from_keys_mixed_single_and_multi_digit_numbers() -> None:
    data = {
        "Prefix_0.suffix": ["value"],
        "Prefix_1.suffix": ["value"],
        "Prefix_10.suffix": ["value"],
        "Prefix_2.suffix": ["value"],
        "Prefix_21.suffix": ["value"],
    }
    assert Utility.find_max_index_from_keys(data) == 21


def test_find_max_index_from_keys_no_matching_keys() -> None:
    data = {
        "NoPrefixOrNumber.suffix": ["value"],
        "AnotherWithoutNumber": ["value"],
    }
    assert Utility.find_max_index_from_keys(data) is None


def test_find_max_index_from_keys_negative_numbers() -> None:
    data = {
        "Prefix_-1.suffix": ["value"],
        "Prefix_-2.suffix": ["value"],
    }
    assert Utility.find_max_index_from_keys(data) is None


def test_find_max_index_from_keys_empty_dictionary() -> None:
    data = {}
    assert Utility.find_max_index_from_keys(data) is None


@pytest.mark.parametrize(
    "test_list,length,expected",
    [
        ([], 3, []),
        ([], 0, []),
        ([1, 2], 1, [1, 2]),
        ([1.0, 2.0], 5, [1.0, 2.0]),
        (["test"], 4, ["test", "test", "test", "test"]),
        ([3], 1, [3]),
        ([5], 5, [5, 5, 5, 5, 5]),
    ],
)
def test_elongate_list(test_list: List[Any], length: int, expected: List[Any]) -> None:
    """Check that lists are elongated correctly."""
    actual = Utility.elongate_list(test_list, length)
    assert actual == expected


@pytest.mark.parametrize(
    "values, expected",
    [
        ([1, 3, 4], True),
        ([0.0, 1.2, 3.8], True),
        ([], True),
        ([-0.1, 0.1], False),
        ([-2, -4], False),
    ],
)
def test_determine_if_all_non_negative_values(values: List[Any], expected: bool) -> None:
    assert Utility.determine_if_all_non_negative_values(values) == expected


@pytest.mark.parametrize(
    "fracs,expected",
    [
        ([0.0, 0.3, 0.99], True),
        ([0.5, 1.0], True),
        ([], True),
        ([-0.01, 0.03], False),
        ([0.4, 1.1], False),
    ],
)
def test_validate_fractions(fracs: List[float], expected: bool) -> None:
    """Tests that all fractions passed are valid."""
    actual = Utility.validate_fractions(fracs)
    assert actual == expected


@pytest.mark.parametrize(
    "input_data, significant_digits, expected_output",
    [
        # Test case 1: List of floats rounded to 3 significant digits
        (
            {"floats_list": [123.456789, 987.654321]},
            3,
            {"floats_list": [123.457, 987.654]},
        ),
        # Test case 2: Mixed list (contains non-numeric values) should remain unchanged
        (
            {"mixed_list": [123.456789, "not_a_number"]},
            3,
            {"mixed_list": [123.456789, "not_a_number"]},
        ),
        # Test case 3: List of integers should remain unchanged
        (
            {"integer_list": [100, 200]},
            3,
            {"integer_list": [100, 200]},
        ),
        # Test case 4: String value should remain unchanged
        (
            {"string_value": "test_string"},
            3,
            {"string_value": "test_string"},
        ),
        # Test case 5: Nested dictionary should remain unchanged
        (
            {"nested_dict": {"key": 42.42}},
            3,
            {"nested_dict": {"key": 42.42}},
        ),
        # Test case 6: Empty dictionary
        (
            {},
            3,
            {},
        ),
        # Test case 7: Dictionary with no numeric values
        (
            {"key": "value"},
            3,
            {"key": "value"},
        ),
        # Test case 8: List of floats rounded to 4 significant digits
        (
            {"nums": [1.23456789, 9.87654321]},
            4,
            {"nums": [1.2346, 9.8765]},
        ),
    ],
)
def test_round_numeric_values_in_dict(
    input_data: dict[str, Any], significant_digits: int, expected_output: dict[str, Any]
) -> None:
    """Tests the round_numeric_values_in_dict() function in Utility"""
    result = Utility.round_numeric_values_in_dict(input_data, significant_digits)
    assert result == expected_output, f"Expected {expected_output}, but got {result}"


@pytest.mark.parametrize(
    "date_format, expected_result",
    [
        ("%j/%Y", True),  # Valid input: Day of Year / Year
        ("%d/%m/%Y", True),  # Valid input: Day / Month / Year
        ("%m/%d/%Y", True),  # Valid input: Month / Day / Year
        ("%b/%d/%Y", True),  # Valid input: Month Abbreviation / Day / Year
        ("%B/%d/%Y", True),  # Valid input: Month full string / Day / Year
        ("%m/%d/%y", True),  # Valid input: Month / Day / Year without century
        ("unknown_format", False),  # Invalid input: String with no '%' directives
        ("", False),  # Edge case: Empty string
        (None, False),  # Edge case: None input
        (12345, False),  # Edge case: Non-string input
        ("This is %m-%d-%Y", True),  # Edge case: String with '%' directives
    ],
)
def test_validate_date_format(date_format: str, expected_result: bool) -> None:
    """Test the `validate_date_format` function with various inputs."""
    assert Utility.validate_date_format(date_format) == expected_result


@pytest.mark.parametrize(
    "user_input, is_valid_format, expected_format",
    [
        ("%j/%Y", True, "%j/%Y"),  # Valid input: Day of Year / Year
        ("%d/%m/%Y", True, "%d/%m/%Y"),  # Valid input: Day / Month / Year
        ("%m/%d/%Y", True, "%m/%d/%Y"),  # Valid input: Month / Day / Year
        ("%b/%d/%Y", True, "%b/%d/%Y"),  # Valid input: Month Abbreviation / Day / Year
        ("%B/%d/%Y", True, "%B/%d/%Y"),  # Valid input: Month full string / Day / Year
        ("%m/%d/%y", True, "%m/%d/%y"),  # Valid input: Month / Day / Year without century
        ("unknown_format", False, "%d/%m/%Y"),  # Invalid input: Default fallback
        ("", False, "%d/%m/%Y"),  # Edge case: Empty string
        (None, False, "%d/%m/%Y"),  # Edge case: None input
        (12345, False, "%d/%m/%Y"),  # Edge case: Non-string input
    ],
)
def test_get_date_formatter(
    user_input: str | None, is_valid_format: bool, expected_format: str, mocker: MockerFixture
) -> None:
    """Test the `get_date_formatter` function with various inputs."""
    mock_validate_date_format = mocker.patch.object(Utility, "validate_date_format", return_value=is_valid_format)

    formatter = Utility.get_date_formatter(user_input)

    if user_input is not None:
        mock_validate_date_format.assert_called_once_with(user_input)
    else:
        mock_validate_date_format.assert_not_called()

    assert formatter.fmt == expected_format
    assert isinstance(formatter, DateFormatter)
    sample_date = datetime.datetime(2024, 1, 1)
    numerical_date = date2num(sample_date)
    formatted_date = formatter(numerical_date)
    expected_date = sample_date.strftime(expected_format)
    assert formatted_date == expected_date


@pytest.mark.parametrize(
    "reference_rate, random_value, expected_result",
    [
        (0.5, 0.3, True),
        (0.5, 0.7, False),
        (1.0, 0.9, True),
        (0.0, 0.1, False),
    ],
)
def test_compare_randomized_rate_less_than(
    reference_rate: float, random_value: float, expected_result: bool, mocker: MockerFixture
) -> None:
    mocker.patch("RUFAS.util.random", return_value=random_value)
    result = Utility.compare_randomized_rate_less_than(reference_rate)
    assert result == expected_result


def test_average_aggregator() -> None:
    assert Aggregator.average([1, 2, 3, 4, 5]) == 3
    assert Aggregator.average([-1, -2, -3, -4, -5]) == -3
    assert Aggregator.average([]) == 0


def test_division_aggregator() -> None:
    assert Aggregator.division([100, 2, 5]) == 10
    assert Aggregator.division([100, -2, 5]) == -10
    assert Aggregator.division([]) is None
    assert Aggregator.division([10]) is None
    assert Aggregator.division([10, 0]) is None


def test_product_aggregator() -> None:
    assert Aggregator.product([1, 2, 3, 4, 5]) == 120
    assert Aggregator.product([-1, 2, -3, 4, -5]) == -120
    assert Aggregator.product([]) == 1


def test_sd_aggregator() -> None:
    assert Aggregator.standard_deviation([2, 4, 4, 4, 5, 5, 7, 9]) == pytest.approx(2)
    assert Aggregator.standard_deviation([-2, -4, -4, -4, -5, -5, -7, -9]) == pytest.approx(2)
    assert Aggregator.standard_deviation([]) == 0


def test_sum_aggregator() -> None:
    assert Aggregator.sum([1, 2, 3, 4, 5]) == 15
    assert Aggregator.sum([-1, -2, -3, -4, -5]) == -15
    assert Aggregator.sum([]) == 0


def test_subtraction_aggregator() -> None:
    assert Aggregator.subtraction([10, 2, 3]) == 5
    assert Aggregator.subtraction([10, -2, -3]) == 15
    assert Aggregator.subtraction([]) is None
    assert Aggregator.subtraction([10]) is None

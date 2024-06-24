import datetime
import re
from typing import Any, Dict, List
import pytest
from pytest import approx, raises
from pytest_mock.plugin import MockerFixture

from RUFAS.util import Utility


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
    arr = []
    del_idx = []
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


def test_convert_list_of_dicts_to_dict_of_lists_empty_list():
    result = Utility.convert_list_of_dicts_to_dict_of_lists([])
    assert result == {}


def test_convert_list_of_dicts_to_dict_of_lists_single_dict():
    input_data = [{"a": 1, "b": 2}]
    expected_result = {"a": [1], "b": [2]}
    result = Utility.convert_list_of_dicts_to_dict_of_lists(input_data)
    assert result == expected_result


def test_convert_list_of_dicts_to_dict_of_lists_multiple_dicts():
    input_data = [{"a": 1, "b": 2}, {"a": 3, "c": 4}]
    expected_result = {"a": [1, 3], "b": [2], "c": [4]}
    result = Utility.convert_list_of_dicts_to_dict_of_lists(input_data)
    assert result == expected_result


def test_convert_list_of_dicts_to_dict_of_lists_empty_values():
    input_data = [{"a": 1, "b": 2}, {"a": None, "b": 3}]
    expected_result = {"a": [1, None], "b": [2, 3]}
    result = Utility.convert_list_of_dicts_to_dict_of_lists(input_data)
    assert result == expected_result


def test_convert_list_of_dicts_to_dict_of_lists_empty_keys():
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
    "data_to_pad,expected",
    [
        (
            {
                "a": {
                    "values": ["a", "b", "c"],
                    "info_maps": [{"simulation_day": 1}, {"simulation_day": 4}, {"simulation_day": 5}],
                },
                "b": {
                    "values": ["d", "e", "f"],
                    "info_maps": [{"simulation_day": 3}, {"simulation_day": 4}, {"simulation_day": 6}],
                },
            },
            {
                "a": {
                    "values": ["a", "a", "a", "b", "c", None],
                    "info_maps": [
                        {"simulation_day": 1},
                        {"simulation_day": 2},
                        {"simulation_day": 3},
                        {"simulation_day": 4},
                        {"simulation_day": 5},
                        {"simulation_day": 6},
                    ],
                },
                "b": {
                    "values": [None, None, "d", "e", "e", "f"],
                    "info_maps": [
                        {"simulation_day": 1},
                        {"simulation_day": 2},
                        {"simulation_day": 3},
                        {"simulation_day": 4},
                        {"simulation_day": 5},
                        {"simulation_day": 6},
                    ],
                },
            },
        ),
        (
            {
                "a": {"values": ["a"], "info_maps": [{"simulation_day": 2}]},
                "b": {"values": ["b", "c"], "info_maps": [{"simulation_day": 3}, {"simulation_day": 4}]},
            },
            {
                "a": {"values": ["a", None, None], "info_maps": [{"simulation_day": 2}, {"simulation_day": 3}, {"simulation_day": 4}]},
                "b": {"values": [None, "b", "c"], "info_maps": [{"simulation_day": 2}, {"simulation_day": 3}, {"simulation_day": 4}]},
            },
        ),
        (
            {
                "a": {"values": ["a", "b"], "info_maps": [{"simulation_day": 1}, {"simulation_day": 2}]},
                "b": {"values": ["c", "d"], "info_maps": [{"simulation_day": 1}, {"simulation_day": 2}]},
            },
            {
                "a": {"values": ["a", "b"], "info_maps": [{"simulation_day": 1}, {"simulation_day": 2}]},
                "b": {"values": ["c", "d"], "info_maps": [{"simulation_day": 1}, {"simulation_day": 2}]},
            },
        ),
        (
            {
                "a": {"values": ["a", "b"], "info_maps": [{"simulation_day": 1}, {"simulation_day": 3}]},
                "b": {"values": ["c", "d"], "info_maps": [{"simulation_day": 1}, {"simulation_day": 3}]},
            },
            {
                "a": {
                    "values": ["a", "a", "b"],
                    "info_maps": [{"simulation_day": 1}, {"simulation_day": 2}, {"simulation_day": 3}],
                },
                "b": {
                    "values": ["c", "c", "d"],
                    "info_maps": [{"simulation_day": 1}, {"simulation_day": 2}, {"simulation_day": 3}],
                },
            },
        ),
    ],
)
def test_pad_temporal_data(
    data_to_pad: dict[str, dict[str, list[Any]]], expected: dict[str, dict[str, list[Any]]]
) -> None:
    """Tests the utility method pad_temporal_data."""
    actual = Utility.pad_temporal_data(data_to_pad)

    assert actual == expected


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

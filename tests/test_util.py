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


@pytest.mark.parametrize(
    "year, day, expected_month",
    [
        (2000, 366, 12),  # leap year
        (2001, 365, 12),  # normal year
        (2000, 60, 2),
        (2001, 60, 3),
    ],
)
def test_day_to_month_conversion(year: int, day: int, expected_month: int):
    """Tests that number of days were converted into months correctly"""
    assert Utility.day_to_month_conversion(day, year) == expected_month


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

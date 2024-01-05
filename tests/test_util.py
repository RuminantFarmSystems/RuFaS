import re

import pytest
from pytest import approx, raises

from RUFAS.util import Utility


def test_query():
    """Unit test for function query in file util.py"""
    pass


def test_get_base_dir():
    """Unit test for function get_base_dir in file util.py"""
    pass


def test_read_json_file():
    """Unit test for function read_json_file in file util.py"""
    pass


def test_LP_solve():
    """Unit test for function LP_solve in file util.py"""
    pass


def test_create_LP_problem():
    """Unit test for function create_LP_problem in file util.py"""
    pass


def test_is_correct_structure():
    """Unit test for function is_correct_structure in file util.py"""
    pass


def test_generate_LP_vars():
    """Unit test for function generate_LP_vars in file util.py"""
    pass


def test_add_LP_constraints():
    """Unit test for function add_LP_constraints in file util.py"""
    pass


def test_solve_with_fastest_solver():
    """Unit test for function solve_with_fastest_solver in file util.py"""
    pass


def test_organize_results():
    """Unit test for function organize_results in file util.py"""
    pass


def test_LP_print():
    """Unit test for function LP_print in file util.py"""
    pass


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


@pytest.mark.parametrize("year, day, expected_month", [
    (2000, 366, 12),  # leap year
    (2001, 365, 12),  # normal year
    (2000, 60, 2),
    (2001, 60, 3)
])
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
    timestamp_with_millis_pattern = (
        r"\d{2}-[A-Za-z]{3}-\d{4}_[A-Za-z]{3}_\d{2}-\d{2}-\d{2}\.\d{6}"
    )
    timestamp_without_millis_pattern = (
        r"\d{2}-[A-Za-z]{3}-\d{4}_[A-Za-z]{3}_\d{2}-\d{2}-\d{2}"
    )

    # Act & Assert
    assert re.match(
        timestamp_with_millis_pattern, Utility.get_timestamp(include_millis=True)
    )
    assert re.match(
        timestamp_without_millis_pattern, Utility.get_timestamp(include_millis=False)
    )

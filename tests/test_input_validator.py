from functools import reduce
from typing import Dict, Any, List
from unittest.mock import patch

import pytest
from pytest_mock import MockerFixture

from RUFAS.elements import ElementsCounter
from RUFAS.input_validator import InputValidator


def mock_input_array_data_for_fix_data() -> Dict[str, Dict[str, Any] | List[Any]]:
    return {
        "element1": [1, 2, 3],
        "element2": [1, 2, 3, 4, 5],
        "element3": [],
        "element4": {
            "element5": [1, 2],
        },
        "element6": [1, 2, 3],
        "element7": [1, 2, 3, 4, 5],
        "element8": [],
        "element9": {
            "element10": [1, 2],
        },
    }


@pytest.mark.parametrize(
    "input_data_value, dummy_variable_properties, expected_result",
    [
        (True, {}, True),
        (False, {}, True),
        ("hello", {}, False),
        (2, {}, False),
        (3.5, {}, False),
        ({}, {}, False),
        ([], {}, False),
        (None, {}, False),
        (None, {"nullable": True}, True),
    ],
)
def test_bool_type_validator(
        input_data_value: bool,
        dummy_variable_properties: Dict[str, Any],
        expected_result: bool,
        mocker: MockerFixture,
) -> None:
    """
    Unit test for function _bool_type_validator in file input_manager.py
    """

    # Arrange
    var_path: list[str | int] = ["dummy_var_path"]
    variable_properties: Dict[str, Any] = dummy_variable_properties
    dummy_properties_key = "dummy_variable_properties"
    dummy_input_data = {"a": 1, "b": 2}
    dummy_counter = mocker.MagicMock(autospec=ElementsCounter)
    unused_bool_input = False
    patch_extract = mocker.patch.object(
        InputValidator, "_extract_input_data_by_key_list", return_value=input_data_value)
    patch_path_to_str = mocker.patch.object(
        InputValidator, "convert_variable_path_to_str", return_value="dummy_name")
    patch_for_add_warning = mocker.patch("RUFAS.input_manager.om.add_warning")

    # Act
    result = InputValidator._bool_type_validator(
        var_path,
        variable_properties,
        dummy_input_data,
        unused_bool_input,
        dummy_properties_key,
        dummy_counter,
        unused_bool_input,
    )

    # Assert
    patch_extract.assert_called_once_with(dummy_input_data, var_path, variable_properties, unused_bool_input)
    if dummy_variable_properties.get("nullable", False) is False:
        patch_path_to_str.assert_called_once_with(var_path)
    if not expected_result:
        patch_for_add_warning.assert_called_once()
    else:
        patch_for_add_warning.assert_not_called()
    assert result == expected_result


@pytest.mark.parametrize(
    "dummy_value, dummy_variable_properties, expected_result, expected_warning_call_count",
    [
        (1, {"minimum": 3, "maximum": 7}, False, 1),
        (3, {"minimum": 3, "maximum": 7}, True, 0),
        (5, {"minimum": 3}, True, 0),
        (7, {"minimum": 3, "maximum": 7}, True, 0),
        (9, {"maximum": 7}, False, 1),
        (-1, {"minimum": 3, "maximum": 7}, False, 1),
        (None, {"maximum": 1, "minimum": 0}, False, 1),
        ("42", {"minimum": 4, "maximum": 32}, False, 1),
        (None, {"nullable": True}, True, 0),
    ],
)
def test_number_type_validator(
        dummy_value: int,
        dummy_variable_properties: Dict[str, int],
        expected_result: bool,
        expected_warning_call_count: int,
        mocker: MockerFixture,
) -> None:
    """Unit test for function _number_type_validator in file input_manager.py"""

    # Arrange
    dummy_var_path: list[str | int] = ["dummy_num"]
    dummy_input_data = {"a": 1}
    dummy_properties_key = "dummy_variable_properties"
    unused_bool_input = False
    dummy_counter = mocker.MagicMock(autospec=ElementsCounter)
    patch_extract = mocker.patch.object(
        InputValidator, "_extract_input_data_by_key_list", return_value=dummy_value)
    patch_path_to_str = mocker.patch.object(
        InputValidator, "convert_variable_path_to_str", return_value="dummy_name")

    add_warning = mocker.patch("RUFAS.output_manager.OutputManager.add_warning")
    result = InputValidator._number_type_validator(
        dummy_var_path,
        dummy_variable_properties,
        dummy_input_data,
        unused_bool_input,
        dummy_properties_key,
        dummy_counter,
        unused_bool_input,
    )

    patch_extract.assert_called_once_with(
        dummy_input_data, dummy_var_path, dummy_variable_properties, unused_bool_input
    )
    if dummy_variable_properties.get("nullable", False) is False:
        patch_path_to_str.assert_called_once_with(dummy_var_path)
    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


@pytest.mark.parametrize(
    "dummy_value, dummy_variable_properties, expected_result, expected_warning_call_count",
    [
        ("cow", {"pattern": r"cow", "minimum_length": 1, "maximum_length": 5}, True, 0),
        ("cow", {"pattern": r".{3}", "minimum_length": 1}, True, 0),
        (
                "COW",
                {"pattern": r"cow", "minimum_length": 1, "maximum_length": 5},
                False,
                1,
        ),
        ("cow", {"minimum_length": 1, "maximum_length": 5}, True, 0),
        ("cow", {"minimum_length": 5}, False, 1),
        ("cow", {"maximum_length": 1}, False, 1),
        (None, {"pattern": r"cow", "minimum_length": 1}, False, 1),
        (42.0, {"pattern": r"cow", "maximum_length": 3}, False, 1),
        (None, {"nullable": True}, True, 0),
    ],
)
def test_string_type_validator(
        dummy_value: int,
        dummy_variable_properties: Dict[str, int],
        expected_result: bool,
        expected_warning_call_count: int,
        mocker: MockerFixture,
) -> None:
    """Unit test for _string_type_validator function in file input_manager.py"""
    var_path: list[str | int] = ["dummy_var_path"]
    dummy_properties_key = "dummy_variable_properties"
    dummy_input_data = {"a": 1, "b": 2}
    dummy_counter = mocker.MagicMock(autospec=ElementsCounter)
    unused_bool_input = False
    patch_extract = mocker.patch.object(
        InputValidator, "_extract_input_data_by_key_list", return_value=dummy_value)
    patch_path_to_str = mocker.patch.object(
        InputValidator, "convert_variable_path_to_str", return_value="dummy_name")
    add_warning = mocker.patch("RUFAS.input_manager.om.add_warning")

    result = InputValidator._string_type_validator(
        var_path,
        dummy_variable_properties,
        dummy_input_data,
        unused_bool_input,
        dummy_properties_key,
        dummy_counter,
        unused_bool_input,
    )

    patch_extract.assert_called_once_with(dummy_input_data, var_path, dummy_variable_properties, unused_bool_input)
    if dummy_variable_properties.get("nullable", False) is False:
        patch_path_to_str.assert_called_once_with(var_path)
    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


@pytest.mark.parametrize(
    "dummy_variable_properties, dummy_element_hierarchy, expected_value, expected_result, expected_warning_call_count",
    [
        (
                {
                    "type": "array",
                    "default": [1, 2, 3, 4, 5],
                    "minimum_length": 5,
                    "maximum_length": 10,
                },
                ["element1"],
                [1, 2, 3, 4, 5],
                True,
                2,
        ),
        (
                {
                    "type": "array",
                    "default": [],
                    "minimum_length": 0,
                    "maximum_length": 5,
                },
                ["element2"],
                [],
                True,
                2,
        ),
        (
                {
                    "type": "array",
                    "default": [1, 2, 3, 4, 5],
                    "minimum_length": 5,
                    "maximum_length": 10,
                },
                ["element3"],
                [1, 2, 3, 4, 5],
                True,
                2,
        ),
        (
                {
                    "type": "array",
                    "default": [1, 2, 3],
                    "minimum_length": 2,
                    "maximum_length": 5,
                },
                ["element4", "element5"],
                [1, 2, 3],
                True,
                2,
        ),
    ],
)
def test_fix_array_type_fixable_data(
        dummy_variable_properties: Dict[str, Any],
        dummy_element_hierarchy: List[str],
        expected_value: List[Any],
        expected_result: bool,
        expected_warning_call_count: int,
        mocker: MockerFixture
) -> None:
    """Unit test for fixable array-type data for _fix_data function in file input_manager.py"""

    dummy_input_data = mock_input_array_data_for_fix_data()
    dummy_properties_key = "dummy_variable_properties"
    add_warning = mocker.patch("RUFAS.output_manager.OutputManager.add_warning")

    result = InputValidator._fix_data(
        dummy_variable_properties,
        dummy_element_hierarchy,
        dummy_input_data,
        dummy_properties_key,
    )

    variable_to_check = reduce(lambda d, key: d[key], dummy_element_hierarchy, dummy_input_data)
    assert variable_to_check == expected_value
    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


@pytest.mark.parametrize(
    "dummy_variable_properties, dummy_element_hierarchy, expected_result, expected_warning_call_count",
    [
        (
            {
                "type": "array",
                "minimum_length": 5,
                "maximum_length": 10,
            },
            ["element6"],
            False,
            0,
        ),
        (
            {
                "type": "array",
                "minimum_length": 0,
                "maximum_length": 5,
            },
            ["element7"],
            False,
            0,
        ),
        (
            {
                "type": "array",
                "minimum_length": 2,
                "maximum_length": 5,
            },
            ["element8"],
            False,
            0,
        ),
        (
            {
                "type": "array",
                "minimum_length": 2,
                "maximum_length": 5,
            },
            ["element9", "element10"],
            False,
            0,
        ),
    ],
)
def test_fix_array_type_critical_data(
    dummy_variable_properties: Dict[str, Any],
    dummy_element_hierarchy: List[str],
    expected_result: bool,
    expected_warning_call_count: int,
    mocker: MockerFixture
) -> None:
    """Unit test for critical array-type data for _fix_data function in file input_manager.py"""

    dummy_input_data = mock_input_array_data_for_fix_data()
    dummy_properties_key = "dummy_variable_properties"

    add_warning = mocker.patch("RUFAS.output_manager.OutputManager.add_warning")

    result = InputValidator._fix_data(
        dummy_variable_properties,
        dummy_element_hierarchy,
        dummy_input_data,
        dummy_properties_key,
    )

    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


def mock_input_string_data_for_fix_data() -> dict[str, dict[str, Any]]:
    return {
        "element1": "muu",
        "element2": "muumuu",
        "element3": "",
        "element4": {
            "element5": "muu",
        },
        "element6": "muu",
        "element7": "muumuu",
        "element8": "",
        "element9": {
            "element10": "muu",
        },
    }


@pytest.mark.parametrize(
    "dummy_variable_properties, dummy_element_hierarchy, expected_value, expected_result, expected_warning_call_count",
    [
        (
            {
                "type": "str",
                "default": "cow",
                "pattern": r"cow",
                "minimum_length": 1,
                "maximum_length": 5,
            },
            ["element1"],
            "cow",
            True,
            2,
        ),
        (
            {
                "type": "str",
                "default": "",
                "minimum_length": 0,
                "maximum_length": 5,
            },
            ["element2"],
            "",
            True,
            2,
        ),
        (
            {
                "type": "str",
                "default": "cow",
                "pattern": r"cow",
                "minimum_length": 2,
                "maximum_length": 5,
            },
            ["element3"],
            "cow",
            True,
            2,
        ),
        (
            {
                "type": "str",
                "default": "cow",
                "pattern": r"cow",
                "minimum_length": 2,
                "maximum_length": 5,
            },
            ["element4", "element5"],
            "cow",
            True,
            2,
        ),
    ],
)
def test_fix_string_type_fixable_data(
    dummy_variable_properties: dict[str, Any],
    dummy_element_hierarchy: list[str],
    expected_value: str,
    expected_result: bool,
    expected_warning_call_count: int,
    mocker: MockerFixture
) -> None:
    """Unit test for fixable string-type data for _fix_data function in file input_manager.py"""

    dummy_input_data = mock_input_string_data_for_fix_data()
    dummy_properties_key = "dummy_variable_properties"

    add_warning = mocker.patch("RUFAS.output_manager.OutputManager.add_warning")
    result = InputValidator._fix_data(
        dummy_variable_properties,
        dummy_element_hierarchy,
        dummy_input_data,
        dummy_properties_key,
    )

    variable_to_check = reduce(lambda d, key: d[key], dummy_element_hierarchy, dummy_input_data)
    assert variable_to_check == expected_value
    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


def test_fix_string_type_csv_data(mocker: MockerFixture) -> None:
    """Unit test for fixable number-type data from a csv array for _fix_data function in file input_manager.py"""

    dummy_input_data = {"element1": [1, 2, 3, 4, 5]}
    dummy_variable_properties = {"type": "number", "maximum": 4, "default": 3}
    dummy_element_hierarchy = ["element1", 4]
    dummy_properties_key = "dummy_variable_properties"

    add_warning = mocker.patch("RUFAS.output_manager.OutputManager.add_warning")
    result = InputValidator._fix_data(
        dummy_variable_properties,
        dummy_element_hierarchy,
        dummy_input_data,
        dummy_properties_key,
    )

    fixed_variable = reduce(lambda d, key: d[key], dummy_element_hierarchy, dummy_input_data)

    assert fixed_variable == 3
    assert result is True
    assert add_warning.call_count == 2

from pathlib import Path
from typing import Dict, Any, List, Union, Optional, Type

import pytest
from unittest.mock import call
from pytest_mock import MockerFixture

from RUFAS.data_validator import DataValidator, ElementState, ElementsCounter, CrossValidator


def mock_input_array_data_for_fix_data() -> dict[str | int, Any] | list[Any]:
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
    dummy_variable_properties: dict[str, Any],
    expected_result: bool,
    mocker: MockerFixture,
) -> None:
    """
    Unit test for function _bool_type_validator in file input_manager.py
    """
    # Arrange
    var_path: list[str | int] = ["dummy_var_path"]
    variable_properties: dict[str, Any] = dummy_variable_properties
    dummy_properties_key = "dummy_variable_properties"
    dummy_input_data: dict[str | int, Any] | list[Any] = {"a": 1, "b": 2}
    dummy_counter = mocker.MagicMock(autospec=ElementsCounter)
    unused_bool_input = False
    patch_extract = mocker.patch.object(DataValidator, "_extract_data_by_key_list", return_value=input_data_value)
    patch_path_to_str = mocker.patch.object(DataValidator, "convert_variable_path_to_str", return_value="dummy_name")

    dv = DataValidator()

    # Act
    result = dv._bool_type_validator(
        var_path,
        variable_properties,
        dummy_input_data,
        unused_bool_input,
        dummy_properties_key,
        dummy_counter,
        unused_bool_input,
        {"string", "number", "bool"},
    )

    # Assert
    patch_extract.assert_called_once_with(dummy_input_data, var_path, variable_properties, unused_bool_input)
    if dummy_variable_properties.get("nullable", False) is False:
        patch_path_to_str.assert_called_once_with(var_path)
    if not expected_result:
        info_map = {
            "class": DataValidator.__name__,
            "function": DataValidator._bool_type_validator.__name__,
        }
        properties_violation_message = (
            f"Violates properties defined in metadata properties section" f" '{dummy_properties_key}'."
        )
        variable_path_str = dv.convert_variable_path_to_str(var_path)
        assert dv.event_logs == [
            {
                "warning": "Validation: bool variable is not a bool",
                "message": (
                    f"Variable: '{variable_path_str}' has value: '{input_data_value}', is type: "
                    f"'{type(input_data_value)}'. {properties_violation_message}"
                ),
                "info_map": info_map,
            }
        ]
    else:
        assert dv.event_logs == []
    assert result == expected_result


@pytest.mark.parametrize(
    "dummy_value, dummy_variable_properties, expected_result",
    [
        (1, {"minimum": 3, "maximum": 7}, False),
        (3, {"minimum": 3, "maximum": 7}, True),
        (5, {"minimum": 3}, True),
        (7, {"minimum": 3, "maximum": 7}, True),
        (9, {"maximum": 7}, False),
        (-1, {"minimum": 3, "maximum": 7}, False),
        (None, {"maximum": 1, "minimum": 0}, False),
        ("42", {"minimum": 4, "maximum": 32}, False),
        (None, {"nullable": True}, True),
    ],
)
def test_number_type_validator(
    dummy_value: int,
    dummy_variable_properties: dict[str, int],
    expected_result: bool,
    mocker: MockerFixture,
) -> None:
    """Unit test for function _number_type_validator in file input_manager.py"""

    # Arrange
    dummy_var_path: list[str | int] = ["dummy_num"]
    dummy_input_data: dict[str | int, Any] | list[Any] = {"a": 1}
    dummy_properties_key = "dummy_variable_properties"
    unused_bool_input = False
    dummy_counter = mocker.MagicMock(autospec=ElementsCounter)
    patch_extract = mocker.patch.object(DataValidator, "_extract_data_by_key_list", return_value=dummy_value)
    patch_path_to_str = mocker.patch.object(DataValidator, "convert_variable_path_to_str", return_value="dummy_name")

    dv = DataValidator()

    result = dv._number_type_validator(
        dummy_var_path,
        dummy_variable_properties,
        dummy_input_data,
        unused_bool_input,
        dummy_properties_key,
        dummy_counter,
        unused_bool_input,
        {"string", "number", "bool"},
    )

    patch_extract.assert_called_once_with(
        dummy_input_data, dummy_var_path, dummy_variable_properties, unused_bool_input
    )
    if dummy_variable_properties.get("nullable", False) is False:
        patch_path_to_str.assert_called_once_with(dummy_var_path)
    assert result == expected_result
    if not expected_result:
        assert len(dv.event_logs) == 1


@pytest.mark.parametrize(
    "dummy_value, dummy_variable_properties, expected_result",
    [
        ("cow", {"pattern": r"cow", "minimum_length": 1, "maximum_length": 5}, True),
        ("cow", {"pattern": r".{3}", "minimum_length": 1}, True),
        (
            "COW",
            {"pattern": r"cow", "minimum_length": 1, "maximum_length": 5},
            False,
        ),
        ("cow", {"minimum_length": 1, "maximum_length": 5}, True),
        ("cow", {"minimum_length": 5}, False),
        ("cow", {"maximum_length": 1}, False),
        (None, {"pattern": r"cow", "minimum_length": 1}, False),
        (42.0, {"pattern": r"cow", "maximum_length": 3}, False),
        (None, {"nullable": True}, True),
    ],
)
def test_string_type_validator(
    dummy_value: int,
    dummy_variable_properties: Dict[str, int],
    expected_result: bool,
    mocker: MockerFixture,
) -> None:
    """Unit test for _string_type_validator function in file input_manager.py"""
    var_path: list[str | int] = ["dummy_var_path"]
    dummy_properties_key = "dummy_variable_properties"
    dummy_input_data: dict[str | int, Any] | list[Any] = {"a": 1, "b": 2}
    dummy_counter = mocker.MagicMock(autospec=ElementsCounter)
    unused_bool_input = False
    patch_extract = mocker.patch.object(DataValidator, "_extract_data_by_key_list", return_value=dummy_value)
    patch_path_to_str = mocker.patch.object(DataValidator, "convert_variable_path_to_str", return_value="dummy_name")

    dv = DataValidator()

    result = dv._string_type_validator(
        var_path,
        dummy_variable_properties,
        dummy_input_data,
        unused_bool_input,
        dummy_properties_key,
        dummy_counter,
        unused_bool_input,
        {"string", "number", "bool"},
    )

    patch_extract.assert_called_once_with(dummy_input_data, var_path, dummy_variable_properties, unused_bool_input)
    if dummy_variable_properties.get("nullable", False) is False:
        patch_path_to_str.assert_called_once_with(var_path)
    assert result == expected_result
    if not expected_result:
        assert len(dv.event_logs) == 1


@pytest.mark.parametrize(
    "dummy_variable_properties, dummy_element_hierarchy, expected_value, expected_result",
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
        ),
    ],
)
def test_fix_array_type_fixable_data(
    dummy_variable_properties: dict[str, Any],
    dummy_element_hierarchy: list[str | int],
    expected_value: list[Any],
    expected_result: bool,
) -> None:
    """Unit test for fixable array-type data for _fix_data function in file input_manager.py"""
    dummy_input_data: dict[str | int, Any] | list[Any] = mock_input_array_data_for_fix_data()
    dummy_properties_key = "dummy_variable_properties"
    properties_violation_message = (
        f"Violates properties defined in metadata properties section '{dummy_properties_key}'."
    )
    variable_parent: dict[str | int, Any] | list[Any] = dummy_input_data
    for key in dummy_element_hierarchy[:-1]:
        if isinstance(variable_parent, list):
            variable_parent = variable_parent[int(key)]
        else:
            variable_parent = variable_parent[key] if isinstance(key, str | int) else variable_parent[str(key)]
    element_path = ".".join([str(element) for element in dummy_element_hierarchy])
    if isinstance(variable_parent, list):
        original_invalid_value = variable_parent[int(dummy_element_hierarchy[-1])]
    else:
        original_invalid_value = variable_parent.get(dummy_element_hierarchy[-1])
    info_map = {
        "class": DataValidator.__name__,
        "function": DataValidator._fix_data.__name__,
    }

    dv = DataValidator()

    result = dv._fix_data(
        dummy_variable_properties,
        dummy_element_hierarchy,
        dummy_input_data,
        dummy_properties_key,
    )

    variable_to_check = dummy_input_data
    for key in dummy_element_hierarchy:
        if isinstance(variable_to_check, list):
            variable_to_check = variable_to_check[int(key)]
        else:
            variable_to_check = variable_to_check[key]
    assert variable_to_check == expected_value
    assert result == expected_result
    assert dv.event_logs == [
        {
            "warning": "Validation: invalid data found",
            "message": f"Variable: '{element_path}' has value:"
            f" {original_invalid_value}. {properties_violation_message}",
            "info_map": info_map,
        },
        {
            "warning": "Validation: data fixed",
            "message": f"Invalid data fixed: '{element_path}' value changed from"
            f" {original_invalid_value} to "
            f"{dummy_variable_properties['default']}. Fix enabled by default value specified in "
            f"'{dummy_properties_key}'.",
            "info_map": info_map,
        },
    ]


@pytest.mark.parametrize(
    "dummy_variable_properties, dummy_element_hierarchy, expected_result",
    [
        (
            {
                "type": "array",
                "minimum_length": 5,
                "maximum_length": 10,
            },
            ["element6"],
            False,
        ),
        (
            {
                "type": "array",
                "minimum_length": 0,
                "maximum_length": 5,
            },
            ["element7"],
            False,
        ),
        (
            {
                "type": "array",
                "minimum_length": 2,
                "maximum_length": 5,
            },
            ["element8"],
            False,
        ),
        (
            {
                "type": "array",
                "minimum_length": 2,
                "maximum_length": 5,
            },
            ["element9", "element10"],
            False,
        ),
    ],
)
def test_fix_array_type_critical_data(
    dummy_variable_properties: dict[str, Any],
    dummy_element_hierarchy: list[str | int],
    expected_result: bool,
) -> None:
    """Unit test for critical array-type data for _fix_data function in file input_manager.py"""
    dummy_input_data: dict[str | int, Any] | list[Any] = mock_input_array_data_for_fix_data()
    dummy_properties_key = "dummy_variable_properties"
    variable_parent: dict[str | int, Any] | list[Any] = dummy_input_data
    for key in dummy_element_hierarchy[:-1]:
        if isinstance(variable_parent, list):
            variable_parent = variable_parent[int(key)]
        else:
            variable_parent = variable_parent[key]
    properties_violation_message = (
        f"Violates properties defined in metadata properties section '{dummy_properties_key}'."
    )
    invalid_value = (
        variable_parent.get(dummy_element_hierarchy[-1], "missing required value")
        if isinstance(variable_parent, dict)
        else variable_parent[int(dummy_element_hierarchy[-1])]
    )
    error_message = (
        f"Variable: '{dummy_element_hierarchy[-1]}' has invalid value: '{invalid_value}'"
        f", and cannot be changed to a default value. {properties_violation_message}"
    )
    info_map = {
        "class": DataValidator.__name__,
        "function": DataValidator._fix_data.__name__,
    }

    dv = DataValidator()

    result = dv._fix_data(
        dummy_variable_properties,
        dummy_element_hierarchy,
        dummy_input_data,
        dummy_properties_key,
    )

    assert result == expected_result
    assert dv.event_logs == [
        {"error": "Validation: invalid data not able to be fixed", "message": error_message, "info_map": info_map}
    ]


def mock_input_string_data_for_fix_data() -> dict[str, str | dict[str, Any]]:
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
    "dummy_variable_properties, dummy_element_hierarchy, expected_value, expected_result",
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
        ),
    ],
)
def test_fix_string_type_fixable_data(
    dummy_variable_properties: dict[str, Any],
    dummy_element_hierarchy: list[str | int],
    expected_value: str,
    expected_result: bool,
) -> None:
    """Unit test for fixable string-type data for _fix_data function in file input_manager.py"""
    dummy_input_data: dict[str | int, Any] | list[Any] = mock_input_array_data_for_fix_data()
    dummy_properties_key = "dummy_variable_properties"
    properties_violation_message = (
        f"Violates properties defined in metadata properties section '{dummy_properties_key}'."
    )
    variable_parent: dict[str | int, Any] | list[Any] = dummy_input_data
    for key in dummy_element_hierarchy[:-1]:
        if isinstance(variable_parent, list):
            variable_parent = variable_parent[int(key)]
        else:
            variable_parent = variable_parent[key]
    element_path = ".".join([str(element) for element in dummy_element_hierarchy])
    if isinstance(variable_parent, list):
        original_invalid_value = variable_parent[int(dummy_element_hierarchy[-1])]
    else:
        original_invalid_value = variable_parent.get(dummy_element_hierarchy[-1])
    info_map = {
        "class": DataValidator.__name__,
        "function": DataValidator._fix_data.__name__,
    }

    dv = DataValidator()

    result = dv._fix_data(
        dummy_variable_properties,
        dummy_element_hierarchy,
        dummy_input_data,
        dummy_properties_key,
    )

    variable_to_check: dict[str | int, Any] | list[Any] = dummy_input_data
    for key in dummy_element_hierarchy:
        if isinstance(variable_to_check, list):
            variable_to_check = variable_to_check[int(key)]
        else:
            variable_to_check = variable_to_check[key]
    assert str(variable_to_check) == expected_value
    assert result == expected_result
    assert dv.event_logs == [
        {
            "warning": "Validation: invalid data found",
            "message": f"Variable: '{element_path}' has value:"
            f" {original_invalid_value}. {properties_violation_message}",
            "info_map": info_map,
        },
        {
            "warning": "Validation: data fixed",
            "message": f"Invalid data fixed: '{element_path}' value changed from"
            f" {original_invalid_value} to "
            f"{dummy_variable_properties['default']}. Fix enabled by default value specified in "
            f"'{dummy_properties_key}'.",
            "info_map": info_map,
        },
    ]


def test_fix_string_type_csv_data() -> None:
    """Unit test for fixable number-type data from a csv array for _fix_data function in file input_manager.py"""
    dummy_input_data: dict[str | int, Any] | list[Any] = {"element1": [1, 2, 3, 4, 5]}
    dummy_variable_properties = {"type": "number", "maximum": 4, "default": 3}
    dummy_element_hierarchy: list[str | int] = ["element1", 4]
    dummy_properties_key = "dummy_variable_properties"
    element_path = ".".join([str(element) for element in dummy_element_hierarchy])
    properties_violation_message = (
        f"Violates properties defined in metadata properties section '{dummy_properties_key}'."
    )
    info_map = {
        "class": DataValidator.__name__,
        "function": DataValidator._fix_data.__name__,
    }
    variable_parent: dict[str | int, Any] | list[Any] = dummy_input_data
    for key in dummy_element_hierarchy[:-1]:
        if isinstance(variable_parent, list):
            variable_parent = variable_parent[int(key)]
        else:
            variable_parent = variable_parent[key]
    if isinstance(variable_parent, list):
        original_invalid_value = variable_parent[int(dummy_element_hierarchy[-1])]
    else:
        original_invalid_value = variable_parent[dummy_element_hierarchy[-1]]

    dv: DataValidator = DataValidator()
    result = dv._fix_data(
        dummy_variable_properties,
        dummy_element_hierarchy,
        dummy_input_data,
        dummy_properties_key,
    )

    fixed_variable = dummy_input_data
    for key in dummy_element_hierarchy:
        if isinstance(fixed_variable, list):
            fixed_variable = fixed_variable[int(key)]
        else:
            fixed_variable = fixed_variable[key]

    assert isinstance(fixed_variable, int)
    assert fixed_variable == 3
    assert result
    assert dv.event_logs == [
        {
            "warning": "Validation: invalid data found",
            "message": f"Variable: '{element_path}' has value:"
            f" {original_invalid_value}. {properties_violation_message}",
            "info_map": info_map,
        },
        {
            "warning": "Validation: data fixed",
            "message": f"Invalid data fixed: '{element_path}' value changed from"
            f" {original_invalid_value} to "
            f"{dummy_variable_properties['default']}. Fix enabled by default value specified in "
            f"'{dummy_properties_key}'.",
            "info_map": info_map,
        },
    ]


@pytest.mark.parametrize(
    "dummy_variable_properties, dummy_element_hierarchy, expected_result",
    [
        (
            {
                "type": "str",
                "pattern": r"cow",
                "minimum_length": 1,
                "maximum_length": 5,
            },
            ["element6"],
            False,
        ),
        (
            {
                "type": "str",
                "pattern": r"cow",
                "minimum_length": 1,
                "maximum_length": 5,
            },
            ["element7"],
            False,
        ),
        (
            {
                "type": "str",
                "pattern": r"cow",
                "minimum_length": 1,
                "maximum_length": 5,
            },
            ["element8"],
            False,
        ),
        (
            {
                "type": "str",
                "pattern": r"cow",
                "minimum_length": 2,
                "maximum_length": 5,
            },
            ["element9", "element10"],
            False,
        ),
    ],
)
def test_fix_string_type_critical_data(
    dummy_variable_properties: dict[str, Any],
    dummy_element_hierarchy: list[str | int],
    expected_result: bool,
) -> None:
    """Unit test for critical string-type data for _fix_data function in file input_manager.py"""
    dummy_input_data = mock_input_array_data_for_fix_data()
    dummy_properties_key = "dummy_variable_properties"
    variable_parent = dummy_input_data
    for key in dummy_element_hierarchy[:-1]:
        variable_parent = variable_parent[key] if isinstance(variable_parent, dict) else variable_parent[int(key)]
    properties_violation_message = (
        f"Violates properties defined in metadata properties section '{dummy_properties_key}'."
    )
    invalid_value = (
        variable_parent.get(str(dummy_element_hierarchy[-1]), "missing required value")
        if isinstance(variable_parent, dict)
        else variable_parent[int(dummy_element_hierarchy[-1])]
    )
    error_message = (
        f"Variable: '{dummy_element_hierarchy[-1]}' has invalid value: '{invalid_value}'"
        f", and cannot be changed to a default value. {properties_violation_message}"
    )
    info_map = {
        "class": DataValidator.__name__,
        "function": DataValidator._fix_data.__name__,
    }

    dv = DataValidator()

    result = dv._fix_data(
        dummy_variable_properties,
        dummy_element_hierarchy,
        dummy_input_data,
        dummy_properties_key,
    )

    assert result == expected_result
    assert dv.event_logs == [
        {"error": "Validation: invalid data not able to be fixed", "message": error_message, "info_map": info_map}
    ]


def mock_input_number_data_for_fix_data() -> Dict[str, Dict[str, int] | int]:
    return {
        "element1": -1,
        "element2": -1,
        "element3": 0,
        "element4": {
            "element5": 15,
        },
        "element6": -1,
        "element7": -1,
        "element8": 0,
        "element9": {
            "element10": 15,
        },
    }


@pytest.mark.parametrize(
    "dummy_variable_properties, dummy_element_hierarchy, expected_value, expected_result",
    [
        (
            {
                "type": "number",
                "default": 5,
                "minimum": 0,
                "maximum": 10,
            },
            ["element1"],
            5,
            True,
        ),
        (
            {
                "type": "number",
                "default": 0,
                "minimum": 0,
                "maximum": 10,
            },
            ["element2"],
            0,
            True,
        ),
        (
            {
                "type": "number",
                "default": 5,
                "minimum": 1,
                "maximum": 10,
            },
            ["element3"],
            5,
            True,
        ),
        (
            {
                "type": "number",
                "default": 5,
                "minimum": 0,
                "maximum": 10,
            },
            ["element4", "element5"],
            5,
            True,
        ),
    ],
)
def test_fix_number_type_fixable_data(
    dummy_variable_properties: dict[str, Any],
    dummy_element_hierarchy: list[str | int],
    expected_value: str,
    expected_result: bool,
) -> None:
    """Unit test for fixable number-type data for _fix_data function in file input_manager.py"""
    dummy_input_data: dict[str | int, Any] | list[Any] = mock_input_array_data_for_fix_data()
    dummy_properties_key = "dummy_variable_properties"
    properties_violation_message = (
        f"Violates properties defined in metadata properties section '{dummy_properties_key}'."
    )
    variable_parent: dict[str | int, Any] | list[Any] = dummy_input_data
    for key in dummy_element_hierarchy[:-1]:
        if isinstance(variable_parent, list):
            variable_parent = variable_parent[int(key)]
        else:
            variable_parent = variable_parent[key]
    element_path = ".".join([str(element) for element in dummy_element_hierarchy])
    if isinstance(variable_parent, list):
        original_invalid_value = variable_parent[int(dummy_element_hierarchy[-1])]
    else:
        original_invalid_value = variable_parent[dummy_element_hierarchy[-1]]
    info_map = {
        "class": DataValidator.__name__,
        "function": DataValidator._fix_data.__name__,
    }

    dv = DataValidator()

    result = dv._fix_data(
        dummy_variable_properties,
        dummy_element_hierarchy,
        dummy_input_data,
        dummy_properties_key,
    )

    variable_to_check = dummy_input_data
    for key in dummy_element_hierarchy:
        if isinstance(variable_to_check, list):
            variable_to_check = variable_to_check[int(key)]
        else:
            variable_to_check = variable_to_check[key]
    assert variable_to_check == expected_value
    assert result == expected_result
    assert dv.event_logs == [
        {
            "warning": "Validation: invalid data found",
            "message": f"Variable: '{element_path}' has value:"
            f" {original_invalid_value}. {properties_violation_message}",
            "info_map": info_map,
        },
        {
            "warning": "Validation: data fixed",
            "message": f"Invalid data fixed: '{element_path}' value changed from"
            f" {original_invalid_value} to "
            f"{dummy_variable_properties['default']}. Fix enabled by default value specified in "
            f"'{dummy_properties_key}'.",
            "info_map": info_map,
        },
    ]


@pytest.mark.parametrize(
    "dummy_variable_properties, dummy_element_hierarchy, expected_result,",
    [
        (
            {
                "type": "number",
                "minimum": 0,
                "maximum": 10,
            },
            ["element6"],
            False,
        ),
        (
            {
                "type": "number",
                "minimum": 0,
                "maximum": 10,
            },
            ["element7"],
            False,
        ),
        (
            {
                "type": "number",
                "minimum": 1,
                "maximum": 10,
            },
            ["element8"],
            False,
        ),
        (
            {
                "type": "number",
                "minimum": 0,
                "maximum": 10,
            },
            ["element9", "element10"],
            False,
        ),
    ],
)
def test_fix_number_type_critical_data(
    dummy_variable_properties: dict[str, Any],
    dummy_element_hierarchy: list[str | int],
    expected_result: bool,
) -> None:
    """Unit test for critical number-type data for _fix_data function in file input_manager.py"""
    dummy_input_data: dict[str | int, Any] | list[Any] = mock_input_array_data_for_fix_data()
    dummy_properties_key = "dummy_variable_properties"
    variable_parent: dict[str | int, Any] | list[Any] = dummy_input_data
    for key in dummy_element_hierarchy[:-1]:
        if isinstance(variable_parent, list):
            variable_parent = variable_parent[int(key)]
        else:
            variable_parent = variable_parent[key]
    properties_violation_message = (
        f"Violates properties defined in metadata properties section '{dummy_properties_key}'."
    )
    invalid_value = (
        variable_parent.get(dummy_element_hierarchy[-1], "missing required value")
        if isinstance(variable_parent, dict)
        else variable_parent[int(dummy_element_hierarchy[-1])]
    )
    error_message = (
        f"Variable: '{dummy_element_hierarchy[-1]}' has invalid value: '{invalid_value}'"
        f", and cannot be changed to a default value. {properties_violation_message}"
    )
    info_map = {
        "class": DataValidator.__name__,
        "function": DataValidator._fix_data.__name__,
    }

    dv = DataValidator()

    result = dv._fix_data(
        dummy_variable_properties,
        dummy_element_hierarchy,
        dummy_input_data,
        dummy_properties_key,
    )

    assert result == expected_result
    assert dv.event_logs == [
        {"error": "Validation: invalid data not able to be fixed", "message": error_message, "info_map": info_map}
    ]


@pytest.mark.parametrize(
    "input_data, variable_path, expected, expected_exception",
    [
        # Success cases
        (
            {
                "animal": {
                    "herd_information": {
                        "calf_num": 8,
                        "heiferI_num": 44,
                        "heiferII_num": 38,
                        "heiferIII_num_springers": 12,
                    }
                }
            },
            ["animal", "herd_information", "calf_num"],
            8,
            None,
        ),
        (
            {
                "manure_management_scenarios": [
                    {"bedding_type": "straw", "manure_handler": "manual scraping"},
                    {"bedding_type": "sawdust", "manure_handler": "flush system"},
                ]
            },
            ["manure_management_scenarios", 0, "bedding_type"],
            "straw",
            None,
        ),
        # Error cases
        (
            {"animal": {"herd_information": {"calf_num": 8}}},
            ["animal", "herd_information", "missing_key"],
            None,
            KeyError,
        ),
        ([{"key": "value"}], [0, "nonexistent_key"], None, KeyError),
    ],
)
def test_extract_value_by_key_list(
    input_data: dict[str | int, Any] | list[Any],
    variable_path: list[Union[str, int]],
    expected: Optional[Any],
    expected_exception: Optional[Type[Exception]],
) -> None:
    """
    Unit test for the _extract_value_by_key_list() method of the InputManager class.
    """
    dv = DataValidator()
    # Act and assert
    if expected_exception:
        with pytest.raises(expected_exception):
            dv.extract_value_by_key_list(input_data, variable_path)
    else:
        result = dv.extract_value_by_key_list(input_data, variable_path)
        assert result == expected


@pytest.mark.parametrize(
    "variable_path, expected",
    [
        (["animal", "herd_information", "calf_num"], "animal.herd_information.calf_num"),
        (["manure_management_scenarios", 0, "bedding_type"], "manure_management_scenarios.[0].bedding_type"),
        ([], ""),
        (["level1", 2, "level3", "4", 5], "level1.[2].level3.[4].[5]"),
        (["single_level"], "single_level"),
        (["multi", "path", "with", "strings"], "multi.path.with.strings"),
        ([0, 1, 2, 3], "[0].[1].[2].[3]"),
    ],
)
def test_convert_variable_path_to_str(variable_path: List[Union[str, int]], expected: str) -> None:
    """
    Unit test for the _convert_variable_path_to_str() method of the InputManager class.
    """
    dv = DataValidator()

    # Act
    result = dv.convert_variable_path_to_str(variable_path)

    # Assert
    assert result == expected


@pytest.mark.parametrize(
    "variable_path, variable_properties, input_data, eager_termination, properties_blob_key,"
    "expected_result, patch_extract_return, patch_validate_return",
    [
        # Test case with valid object data
        (
            ["data", "object"],
            {"key": {"type": "string"}},
            {"data": {"object": {"key": "value"}}},
            False,
            "blob_key",
            True,
            {"key": "value"},
            True,
        ),
        # Test case with invalid object data
        (
            ["data", "object"],
            {"key": {"type": "string"}},
            {"data": {"object": "not_a_dict"}},
            False,
            "blob_key",
            False,
            "not_a_dict",
            False,
        ),
        (
            ["data", "object", "nested"],
            {"nested": {"type": "object", "properties": {"key": {"type": "string"}}}},
            {"data": {"object": {"nested": {"key": 123}}}},
            False,
            "blob_key",
            False,
            {"nested": {"key": 123}},
            False,
        ),
        (
            ["data", "early_failure"],
            {"description": "a description", "key1": {"type": "string"}, "key2": {"type": "integer"}},
            {"data": {"early_failure": {"key1": "valid", "key2": "not_an_integer"}}},  # key2 fails validation
            True,
            "blob_key",
            False,
            {"key1": "valid", "key2": "not_an_integer"},
            False,
        ),
    ],
)
def test_object_type_validator(
    mocker: MockerFixture,
    variable_path: list[Union[str, int]],
    variable_properties: dict[str, Any],
    input_data: dict[str | int, Any] | list[Any],
    eager_termination: bool,
    properties_blob_key: str,
    expected_result: bool,
    patch_extract_return: Any,
    patch_validate_return: bool,
) -> None:
    """
    Unit test for the _object_type_validator() method of the InputManager class.
    """

    # Arrange
    mocker.patch.object(DataValidator, "_extract_data_by_key_list", return_value=patch_extract_return)
    mocker.patch.object(DataValidator, "validate_data_by_type", return_value=patch_validate_return)
    mock_elements_counter = mocker.MagicMock()
    dv = DataValidator()

    # Act
    result = dv._object_type_validator(
        variable_path,
        variable_properties,
        input_data,
        eager_termination,
        properties_blob_key,
        mock_elements_counter,
        True,
        {"string", "number", "bool"},
    )

    # Assert
    assert result == expected_result


@pytest.mark.parametrize(
    "data,removed_keys",
    [
        ({"key1": {}, "key2": {}}, []),
        ({"key1": {}, "key2": {}, "key3": {}}, ["key3"]),
        ({"k1": {}, "k2": {}, "k3": {}}, ["k1", "k2", "k3"]),
    ],
)
def test_object_type_validator_key_removal(
    mocker: MockerFixture, data: dict[str, Any], removed_keys: list[str]
) -> None:
    """Tests that extraneous keys are properly removed by the _object_type_validator in Input Manager."""
    mocker.patch.object(DataValidator, "_extract_data_by_key_list", return_value=data)
    mocker.patch.object(DataValidator, "validate_data_by_type", return_value=True)
    mocker.patch.object(DataValidator, "convert_variable_path_to_str", return_value="dummy path")

    mock_elements_counter = mocker.MagicMock()
    variable_properties: dict[str, Any] = {"key1": {}, "key2": {}}
    violation_msg = "Violates properties defined in metadata properties section 'properties blob'."
    info_map = {"class": "DataValidator", "function": "_object_type_validator"}
    dv = DataValidator()
    expected_event_log = [
        {
            "warning": "Validation: object contains extraneous data",
            "message": (
                f"Variable: 'dummy path' contains data at key '{key}' "
                f"that is not specified in the metadata properties. {violation_msg}"
            ),
            "info_map": info_map,
        }
        for key in removed_keys
    ]

    result = dv._object_type_validator(
        ["path", "to", "var"],
        variable_properties,
        {"dummy": "data"},
        False,
        "properties blob",
        mock_elements_counter,
        True,
        {"string", "number", "bool"},
    )

    assert result
    assert dv.event_logs == expected_event_log


@pytest.mark.parametrize(
    "variable_path, variable_properties, input_data, properties_blob_key," "expected_result, expected_warning",
    [
        # Input data is not a list
        (
            ["data", "array"],
            {"maximum_length": 5, "minimum_length": 1},
            "not_a_list",
            "blob_key",
            False,
            "Validation: array container is not a list",
        ),
        # Input list's length is less than the specified minimum length
        (
            ["data", "array"],
            {"maximum_length": 5, "minimum_length": 2},
            [1],
            "blob_key",
            False,
            "Validation: array length less than minimum",
        ),
        # Input list's length exceeds the specified maximum length
        (
            ["data", "array"],
            {"maximum_length": 3, "minimum_length": 1},
            [1, 2, 3, 4],
            "blob_key",
            False,
            "Validation: array length greater than maximum",
        ),
        # Input list's length is within the specified constraints
        (
            ["data", "array"],
            {"maximum_length": 5, "minimum_length": 1},
            [1, 2, 3],
            "blob_key",
            True,
            None,
        ),
    ],
)
def test_validate_array_container_properties(
    mocker: MockerFixture,
    variable_path: List[Union[str, int]],
    variable_properties: Dict[str, Any],
    input_data: Any,
    properties_blob_key: str,
    expected_result: bool,
    expected_warning: str,
) -> None:
    """
    Unit test for the _validate_array_container_properties() method of the InputManager class.
    """
    info_map = {
        "class": DataValidator.__name__,
        "function": DataValidator._validate_array_container_properties.__name__,
    }
    dv = DataValidator()
    # Act
    result = dv._validate_array_container_properties(
        variable_path, variable_properties, input_data, properties_blob_key
    )

    # Assert
    assert result == expected_result
    if expected_warning:
        assert dv.event_logs == [{"warning": expected_warning, "message": mocker.ANY, "info_map": info_map}]
    else:
        assert dv.event_logs == []


@pytest.mark.parametrize(
    "variable_path, variable_properties, input_data, eager_termination, properties_blob_key,"
    "patch_extract_return, patch_container_valid, patch_element_valid, expected_result",
    [
        # Array extraction returns a non-list
        (
            ["data", "array"],
            {"properties": {"type": "integer"}},
            {},
            False,
            "blob_key",
            None,
            False,
            True,
            False,
        ),
        # Array container properties are invalid
        (
            ["data", "array"],
            {"properties": {"type": "integer"}},
            {"data": {"array": [1, 2, 3]}},
            False,
            "blob_key",
            [1, 2, 3],
            False,
            True,
            False,
        ),
        # Element validation within the array fails
        (
            ["data", "array"],
            {"properties": {"type": "integer"}},
            {"data": {"array": [1, "two", 3]}},
            False,
            "blob_key",
            [1, "two", 3],
            True,
            False,
            False,
        ),
        # Successful validation of all elements
        (
            ["data", "array"],
            {"properties": {"type": "integer"}},
            {"data": {"array": [1, 2, 3]}},
            False,
            "blob_key",
            [1, 2, 3],
            True,
            True,
            True,
        ),
        # Eager termination on element validation failure
        (
            ["data", "array"],
            {"properties": {"type": "integer"}},
            {"data": {"array": [1, "two", 3]}},
            True,
            "blob_key",
            [1, "two", 3],
            True,
            False,
            False,
        ),
        # Nullable array that is None
        (
            ["data", "array"],
            {"properties": {"type": "integer"}, "nullable": True},
            {"data": {"array": None}},
            False,
            "blob_key",
            None,
            True,
            True,
            True,
        ),
        # Nullable and null data passed
        (
            ["data", "array"],
            {"nullable": True},
            {"data": {"array": None}},
            True,
            "blob_key",
            None,
            False,
            False,
            True,
        ),
        # Not nullable and null data passed
        (
            ["data", "array"],
            {},
            {"data": {"array": None}},
            True,
            "blob_key",
            None,
            False,
            False,
            False,
        ),
    ],
)
def test_array_type_validator(
    mocker: MockerFixture,
    variable_path: list[str | int],
    variable_properties: dict[str, Any],
    input_data: dict[str | int, Any] | list[Any],
    eager_termination: bool,
    properties_blob_key: str,
    patch_extract_return: Any,
    patch_container_valid: bool,
    patch_element_valid: bool,
    expected_result: bool,
) -> None:
    """
    Unit test for the _array_type_validator() method of the InputManager class.
    """

    # Arrange
    mocker.patch.object(DataValidator, "_extract_data_by_key_list", return_value=patch_extract_return)
    mocker.patch.object(DataValidator, "_validate_array_container_properties", return_value=patch_container_valid)
    mocker.patch.object(DataValidator, "validate_data_by_type", return_value=patch_element_valid)
    mock_elements_counter = mocker.MagicMock()

    dv = DataValidator()

    # Act
    result = dv._array_type_validator(
        variable_path,
        variable_properties,
        input_data,
        eager_termination,
        properties_blob_key,
        mock_elements_counter,
        True,
        {"string", "number", "bool"},
    )

    # Assert
    assert result == expected_result


@pytest.mark.parametrize(
    "data_type, input_value, expected_result, validator_return, fixable, fix_attempted, simple_type",
    [
        # Primitive data type: valid string
        ("string", "valid string", True, True, False, False, True),
        # Primitive data type: invalid string, fixable
        ("string", "invalid string", True, False, True, True, True),
        # Primitive data type: invalid string, not fixable
        ("string", "invalid string", False, False, False, True, True),
        # Primitive data type: valid number
        ("number", 123, True, True, False, False, True),
        # Primitive data type: invalid number, fixable
        ("number", "invalid number", True, False, True, True, True),
        # Primitive data type: invalid number, not fixable
        ("number", "invalid number", False, False, False, True, True),
        # Primitive data type: valid bool
        ("bool", True, True, True, False, False, True),
        # Primitive data type: invalid bool, fixable
        ("bool", "invalid bool", True, False, True, True, True),
        # Primitive data type: invalid bool, not fixable
        ("bool", "invalid bool", False, False, False, True, True),
        # Complex data type: object, valid
        ("object", {"key": "value"}, True, True, False, False, False),
        # Complex data type: object, invalid
        ("object", "not a dict", False, False, False, False, False),
        # Complex data type: array, valid
        ("array", [1, 2, 3], True, True, False, False, False),
        # Complex data type: array, invalid
        ("array", "not a list", False, False, False, False, False),
    ],
)
def test_validate_input_by_type(
    mocker: MockerFixture,
    data_type: str,
    input_value: Any,
    expected_result: bool,
    validator_return: bool,
    fixable: bool,
    fix_attempted: bool,
    simple_type: bool,
) -> None:
    """
    Unit test for the _validate_input_by_type method of the InputManager class.
    """

    # Arrange
    variable_properties = {"type": data_type}
    variable_path: List[Union[str, int]] = ["path", "to", "variable"]
    input_data: dict[str | int, Any] | list[Any] = {"path": {"to": {"variable": input_value}}}
    eager_termination = False
    properties_blob_key = "blobKey"
    elements_counter = mocker.MagicMock()

    mocker.patch.object(DataValidator, "extract_value_by_key_list", return_value=input_value)
    mocker.patch.object(DataValidator, "convert_variable_path_to_str", return_value="path.to.variable")
    patch_for_fix_data = mocker.patch.object(DataValidator, "_fix_data", return_value=fixable)

    validator_mock = mocker.patch.object(DataValidator, f"_{data_type}_type_validator", return_value=validator_return)
    dv = DataValidator()
    # Act
    result = dv.validate_data_by_type(
        variable_properties,
        variable_path,
        input_data,
        eager_termination,
        properties_blob_key,
        elements_counter,
        True,
        {"string", "number", "bool"},
    )

    # Assert
    assert result == expected_result
    validator_mock.assert_called_once()

    if fix_attempted:
        patch_for_fix_data.assert_called_once()
    else:
        patch_for_fix_data.assert_not_called()

    if not simple_type:
        elements_counter.increment.assert_not_called()
    elif expected_result and not fix_attempted:
        elements_counter.increment.assert_called_once_with(ElementState.VALID)
    elif fixable:
        elements_counter.increment.assert_called_once_with(ElementState.FIXED)
    else:
        elements_counter.increment.assert_called_once_with(ElementState.INVALID)


def test_validate_input_by_type_key_error() -> None:
    variable_properties = {"a": "b"}
    variable_path: list[Union[str, int]] = ["valid_key"]
    properties_blob_key = "dummy_properties_blob_key"
    input_data: dict[str | int, Any] | list[Any] = {"valid_key": {"another_valid_key": "value"}}
    eager_termination = False
    elements_counter = ElementsCounter()
    dv = DataValidator()

    # Act and Assert
    with pytest.raises(KeyError):
        dv.validate_data_by_type(
            variable_properties,
            variable_path,
            input_data,
            eager_termination,
            properties_blob_key,
            elements_counter,
            True,
            {"string", "number", "bool"},
        )


@pytest.mark.parametrize(
    "does_file_exist, metadata, expected_exception",
    [
        (
            True,
            {"files": {"file1": {"path": "valid/path/to/file1.csv", "type": "csv", "properties": "some properties"}}},
            False,
        ),
        (
            False,
            {"files": {"file1": {"path": "valid/path/to/file1.json", "type": "json", "properties": "some properties"}}},
            True,
        ),
        (
            True,
            {
                "files": {
                    "file1": {
                        "path": "valid/path/to/file1.txt",
                        "type": "invalid_type",
                        "properties": "some properties",
                    }
                }
            },
            True,
        ),
        (True, {"files": {"file1": {"path": "valid/path/to/file1.json", "properties": "some properties"}}}, True),
        (
            True,
            {
                "files": {
                    "file1": {
                        "path": "valid/path/to/file1.json",
                        "type": "json",
                        "properties": "some properties",
                        "extra_key": "extra_value",
                    }
                }
            },
            True,
        ),
        (
            True,
            {
                "files": {
                    "file1": {
                        "paths": ["valid/path/to/file1.json", "valid/path/to/file2.json"],
                        "type": "json",
                        "properties": "some properties",
                    }
                }
            },
            False,
        ),
        (
            True,
            {
                "files": {
                    "file1": {
                        "paths": [],
                        "type": "json",
                        "properties": "some properties",
                    }
                }
            },
            True,
        ),
        (
            True,
            {
                "files": {
                    "file1": {"paths": "valid/path/to/file1.json", "type": "json", "properties": "some properties"}
                }
            },
            True,
        ),
        (
            True,
            {
                "files": {
                    "file1": {
                        "paths": ["valid/path/to/file1.json", None],
                        "type": "json",
                        "properties": "some properties",
                    }
                }
            },
            True,
        ),
        (
            False,
            {
                "files": {
                    "file1": {
                        "paths": ["valid/path/to/file1.json", "valid/path/to/file2.json"],
                        "type": "json",
                        "properties": "some properties",
                    }
                }
            },
            True,
        ),
        (
            True,
            {
                "files": {
                    "file1": {
                        "path": "valid/path/to/file1.json",
                        "type": "json",
                        "properties": "",
                    }
                }
            },
            True,
        ),
        (
            True,
            {"files": {"file1": {"path": "", "type": "json", "properties": "some properties"}}},
            True,
        ),
        (
            True,
            {"files": {"file1": {"path": 123, "type": "json", "properties": "some properties"}}},
            True,
        ),
    ],
)
def test_validate_metadata(
    mocker: MockerFixture,
    does_file_exist: bool,
    metadata: dict[str, Any],
    expected_exception: bool,
) -> None:
    mocker.patch("os.path.isfile", return_value=does_file_exist)
    info_map = {
        "class": DataValidator.__name__,
        "function": DataValidator.validate_metadata.__name__,
    }
    dv = DataValidator()

    if expected_exception:
        valid, message = dv.validate_metadata(metadata, {"json", "csv"}, "files", Path(""))
        assert not valid
        assert dv.event_logs == [{"error": "Metadata Validation", "message": mocker.ANY, "info_map": info_map}]
    else:
        dv.validate_metadata(metadata, {"json", "csv"}, "files", Path(""))
        assert dv.event_logs == [
            {"log": "Metadata Validation", "message": "Top level metadata is valid.", "info_map": info_map}
        ]


@pytest.mark.parametrize(
    "metadata, limit, expected_depth, expected_path, should_raise, expected_error, expected_err_msg",
    [
        ({"properties": {"a": {"type": "number"}}}, 2, 1, ["a"], False, [], ""),
        (
            {"properties": {"a": {"b": {"type": "array", "properties": {}}}}},
            3,
            3,
            ["a", "b", "properties"],
            False,
            "None",
            "",
        ),
        (
            {"properties": {"a": {"b": {"c": {"type": "bool"}}}}},
            2,
            3,
            ["a", "b", "c"],
            True,
            "Max metadata depth exceeded.",
            "Metadata depth exceeds maximum allowed depth of 2 at path ['a', 'b', 'c']",
        ),
        ({"properties": {"a": {"b": {"c": {"type": "string"}}}}}, 3, 3, ["a", "b", "c"], False, [], ""),
        (
            {"properties": {"a": {"b": {"type": "invalid_type"}}}},
            3,
            2,
            ["a", "b"],
            True,
            "Properties value type error",
            "Properties 'type' value not in ['number', 'array', 'bool', 'string', 'object']",
        ),
        (
            {"properties": {"a": {"b": {"c": {"type": "object", "unique_key": "yes"}}}}},
            3,
            3,
            ["a", "b", "c"],
            False,
            "None",
            "",
        ),
    ],
)
def test_validate_properties(
    mocker: MockerFixture,
    metadata: Dict[str, Any],
    limit: int,
    expected_depth: int,
    expected_path: List[str],
    should_raise: bool,
    expected_error: str,
    expected_err_msg: str,
) -> None:
    """Tests _validate_properties() function in InputManager."""
    # Initiated to avoid the call of add_log in __init__ to be recorded
    dv = DataValidator()

    info_map = {
        "class": DataValidator.__name__,
        "function": DataValidator.validate_properties.__name__,
    }

    if should_raise:
        valid, exc_info = dv.validate_properties(metadata, limit)
        assert exc_info == expected_err_msg
        assert not valid
        assert dv.event_logs == [{"error": expected_error, "message": mocker.ANY, "info_map": info_map}]
    else:
        valid, exc_info = dv.validate_properties(metadata, limit)
        assert valid
        assert dv.event_logs == [
            {
                "log": "Metadata properties depth",
                "message": f"Max depth of metadata properties is {expected_depth}",
                "info_map": info_map,
            },
            {
                "log": "Metadata properties path",
                "message": f"Deepest path of metadata properties is {expected_path}",
                "info_map": info_map,
            },
        ]


@pytest.mark.parametrize(
    "key_path,value,error_title,error_msg,should_raise",
    [
        (
            ["some_key"],
            {"default": "not_a_number", "minimum": 3, "maximum": 7},
            "Invalid metadata default number value.",
            "Invalid 'default' for '['some_key']': Expected a number but got <class 'str'>.",
            True,
        ),
        (
            ["some_key"],
            {"default": 5, "minimum": "not_a_number", "maximum": 7},
            "Invalid metadata number properties minimum.",
            "Invalid 'minimum' for '['some_key']': Expected a number but got <class 'str'>.",
            True,
        ),
        (
            ["some_key"],
            {"default": 5, "minimum": 3, "maximum": "not_a_number"},
            "Invalid metadata number properties maximum.",
            "Invalid 'maximum' for '['some_key']': Expected a number but got <class 'str'>.",
            True,
        ),
        (
            ["some_key"],
            {"default": 2, "minimum": 3, "maximum": 7},
            "Invalid metadata default.",
            "Invalid 'default' for '['some_key']': 'default' 2 is less than 'minimum' 3",
            True,
        ),
        (
            ["some_key"],
            {"default": 8, "minimum": 3, "maximum": 7},
            "Invalid metadata default.",
            "Invalid 'default' for '['some_key']': 'default' 8 is greater than 'maximum' 7",
            True,
        ),
        (
            ["some_key"],
            {"minimum": 5, "maximum": 3},
            "Invalid range of acceptable numbers.",
            "Invalid 'range' for key '['some_key']': 'minimum' value 5 is greater than 'maximum' value 3",
            True,
        ),
        (["some_key"], {"default": 5, "minimum": 3, "maximum": 8}, "", "", False),
        (
            ["some_key"],
            {"default": None, "minimum": 3, "maximum": 8},
            "Invalid metadata default number value.",
            "Invalid 'default' for '['some_key']': Value is not nullable and default is 'None'.",
            True,
        ),
    ],
)
def test_metadata_number_validator(
    mocker: MockerFixture,
    key_path: List[str],
    value: Dict[str, Any],
    error_title: str,
    error_msg: str,
    should_raise: bool,
) -> None:
    """Tests metadata_number_validator() method in InputManager"""
    mock_validate_properties_keys = mocker.patch(
        "RUFAS.data_validator.DataValidator._validate_metadata_properties_keys", return_value=(True, "")
    )
    dv = DataValidator()
    info_map = {"class": "DataValidator", "function": "_metadata_number_validator"}
    if should_raise:
        valid, msg = dv._metadata_number_validator(key_path, value)
        assert not valid
        assert dv.event_logs == [{"error": error_title, "message": error_msg, "info_map": info_map}]
        mock_validate_properties_keys.assert_called_once()
    else:
        dv._metadata_number_validator(key_path, value)
        mock_validate_properties_keys.assert_called_once()


@pytest.mark.parametrize(
    "key_path,value,error_title,error_msg,should_raise",
    [
        (
            ["some_key"],
            {"default": 123, "pattern": None},
            "Invalid metadata default string value.",
            "Invalid 'default' for '['some_key']': Expected a string but got <class 'int'>",
            True,
        ),
        (
            ["some_key"],
            {"default": "abcdef", "pattern": r"^[0-9]+$"},
            "Invalid metadata default string value.",
            "Invalid 'default' for '['some_key']': 'default' value 'abcdef' does not match pattern ^[0-9]+$",
            True,
        ),
        (
            ["some_key"],
            {"default": None},
            "Invalid metadata default string value.",
            "Invalid 'default' for '['some_key']': Value is not nullable and default is 'None'",
            True,
        ),
        (
            ["some_key"],
            {"default": "abcdef", "pattern": 6789},
            "Invalid metadata string properties pattern.",
            "Invalid 'pattern' for '['some_key']': Expected a string but got <class 'int'>",
            True,
        ),
        (["some_key"], {"default": "12345", "pattern": r"^[0-9]+$"}, "", "", False),
        (["some_key"], {"default": "", "pattern": r"^[0-9]+$"}, "", "", False),
        (
            ["some_key"],
            {"default": "abcdef", "pattern": r"["},
            "Invalid metadata string properties pattern.",
            "Invalid 'pattern' for '['some_key']': 'pattern' value '[' is not a valid regex pattern.",
            True,
        ),
    ],
)
def test_metadata_string_validator(
    mocker: MockerFixture,
    key_path: List[str],
    value: Dict[str, Any],
    error_title: str,
    error_msg: str,
    should_raise: bool,
) -> None:
    """Tests _metadata_string_validator() method in InputManager"""
    mock_validate_properties_keys = mocker.patch(
        "RUFAS.data_validator.DataValidator._validate_metadata_properties_keys", return_value=(True, "")
    )
    dv = DataValidator()
    info_map = {"class": "DataValidator", "function": "_metadata_string_validator"}
    if should_raise:
        valid, msg = dv._metadata_string_validator(key_path, value)
        assert not valid
        assert dv.event_logs == [{"error": error_title, "message": error_msg, "info_map": info_map}]
        mock_validate_properties_keys.assert_called_once()
    else:
        dv._metadata_string_validator(key_path, value)
        mock_validate_properties_keys.assert_called_once()


@pytest.mark.parametrize(
    "key_path,value,error_title,error_msg,should_raise",
    [
        (
            ["some_key"],
            {"default": "not_a_bool"},
            "Invalid metadata default bool value.",
            "Invalid 'default' for '['some_key']': Expected a bool but got <class 'str'>",
            True,
        ),
        (
            ["some_key"],
            {"default": 1},
            "Invalid metadata default bool value.",
            "Invalid 'default' for '['some_key']': Expected a bool but got <class 'int'>",
            True,
        ),
        (["some_key"], {"default": True}, "", "", False),
        (
            ["some_key"],
            {"default": None},
            "Invalid metadata default bool value.",
            "Invalid 'default' for '['some_key']': Value is not nullable and default is 'None'",
            True,
        ),
    ],
)
def test_metadata_bool_validator(
    mocker: MockerFixture,
    key_path: List[str],
    value: Dict[str, Any],
    error_title: str,
    error_msg: str,
    should_raise: bool,
) -> None:
    """Tests _metadata_bool_validator() method in InputManager"""
    mock_validate_properties_keys = mocker.patch(
        "RUFAS.data_validator.DataValidator._validate_metadata_properties_keys", return_value=(True, "")
    )
    dv: DataValidator = DataValidator()
    info_map = {"class": "DataValidator", "function": "_metadata_bool_validator"}
    if should_raise:
        valid, msg = dv._metadata_bool_validator(key_path, value)
        assert not valid
        assert dv.event_logs == [{"error": error_title, "message": error_msg, "info_map": info_map}]
        mock_validate_properties_keys.assert_called_once()
    else:
        dv._metadata_bool_validator(key_path, value)
        mock_validate_properties_keys.assert_called_once()


@pytest.mark.parametrize(
    "key_path,value,error_title,error_msg,should_raise",
    [
        (
            ["some_key"],
            {"minimum_length": 5, "maximum_length": 3},
            "Invalid metadata array length range.",
            "Invalid length 'range' for key '['some_key']': 'minimum_length'"
            " value 5 is greater than 'maximum_length' value 3",
            True,
        ),
        (
            ["some_key"],
            {"minimum_length": "five"},
            "Invalid metadata default array minimum length.",
            "Invalid 'minimum_length' for '['some_key']':" " Expected a number but got <class 'str'>",
            True,
        ),
        (
            ["some_key"],
            {"maximum_length": "three"},
            "Invalid metadata default array maximum length.",
            "Invalid 'maximum_length' for '['some_key']':" " Expected a number but got <class 'str'>",
            True,
        ),
        (["some_key"], {"minimum_length": 1, "maximum_length": 5}, "", "", False),
    ],
)
def test_metadata_array_validator(
    mocker: MockerFixture,
    key_path: List[str],
    value: Dict[str, Any],
    error_title: str,
    error_msg: str,
    should_raise: bool,
) -> None:
    """Tests _metadata_array_validator() method in InputManager"""
    mock_validate_properties_keys = mocker.patch(
        "RUFAS.data_validator.DataValidator._validate_metadata_properties_keys", return_value=(True, "")
    )
    dv = DataValidator()
    info_map = {"class": "DataValidator", "function": "_metadata_array_validator"}
    if should_raise:
        valid, msg = dv._metadata_array_validator(key_path, value)
        assert not valid
        assert dv.event_logs == [{"error": error_title, "message": error_msg, "info_map": info_map}]
        mock_validate_properties_keys.assert_called_once()
    else:
        dv._metadata_array_validator(key_path, value)
        mock_validate_properties_keys.assert_called_once()


def test_metadata_object_validator(
    mocker: MockerFixture,
) -> None:
    """Tests _metadata_object_validator() method in InputManager"""
    mock_validate_properties_keys = mocker.patch(
        "RUFAS.data_validator.DataValidator._validate_metadata_properties_keys", return_value=(True, "")
    )
    key_path = ["path", "cow"]
    value = {"type": "object", "description": "cow", "cow": {"data_about_cow": 17}}
    dv = DataValidator()
    valid, msg = dv._metadata_object_validator(key_path, value)
    assert valid
    mock_validate_properties_keys.assert_called_once()


@pytest.mark.parametrize(
    "required_keys, valid_keys, properties, path, should_raise, expected_message",
    [
        ({"id", "type"}, {"id", "name", "type"}, {"type": "num", "id": 123, "name": "example"}, ["root"], False, ""),
        (
            {"type"},
            {"type"},
            {"type": "num", "id": 123},
            ["root"],
            True,
            "Invalid keys ['id'] in num for ['root']. Valid keys are ['type'].",
        ),
        (
            {"id"},
            set(),
            {"type": "num", "name": "example"},
            ["root"],
            True,
            "Missing required keys ['id'] for ['root']. Required keys are ['id'].",
        ),
        (
            {"id", "type"},
            {"id", "type"},
            {"type": "num", "id": 123, "extra": "data"},
            ["root", "child"],
            True,
            "Invalid keys ['extra'] in num for ['root', 'child']. Valid keys are ['id', 'type'].",
        ),
        (
            {"id", "type"},
            {"id", "type"},
            {"name": "example"},
            ["root"],
            True,
            "Missing required keys ['id', 'type'] for ['root']. Required keys are ['id', 'type'].",
        ),
        (
            {"type"},
            {"type"},
            {"type": "object"},
            ["root"],
            True,
            "No unique keys for ['root']. At least one unique key is expected.",
        ),
    ],
)
def test_validate_metadata_properties_keys(
    mocker: MockerFixture,
    required_keys: set[str],
    valid_keys: set[str],
    properties: dict[str, Any],
    path: list[str],
    should_raise: bool,
    expected_message: str,
) -> None:
    """Test the validation of validate_metadata_properties_keys"""
    dv = DataValidator()

    if should_raise:
        valid, msg = dv._validate_metadata_properties_keys(required_keys, valid_keys, properties, path)
        assert not valid
        assert dv.event_logs == [
            {
                "error": "Metadata Validation",
                "message": expected_message,
                "info_map": {
                    "class": "DataValidator",
                    "function": "_validate_metadata_properties_keys",
                },
            }
        ]
    else:
        valid, msg = dv._validate_metadata_properties_keys(required_keys, valid_keys, properties, path)
        assert valid
        assert dv.event_logs == []


def test_extract_input_data_by_key_list_no_error(mocker: MockerFixture) -> None:
    """Unit tests for making sure data were extracted when no error"""
    dummy_input_data: dict[str | int, Any] | list[Any] = {"a": 1, "b": 2}
    dummy_var_path: list[str | int] = ["dummy_var_path"]
    dummy_var_properties: dict[str, Any] = {"pattern": r"cow", "minimum_length": 1, "maximum_length": 5}
    dummy_value = 1
    patch_extract = mocker.patch.object(DataValidator, "extract_value_by_key_list", return_value=dummy_value)
    patch_log_missing_data = mocker.patch.object(DataValidator, "_log_missing_data")
    dv = DataValidator()

    result = dv._extract_data_by_key_list(
        data=dummy_input_data,
        variable_path=dummy_var_path,
        variable_properties=dummy_var_properties,
        called_during_initialization=True,
    )

    assert result == dummy_value
    patch_log_missing_data.assert_not_called()

    result = dv._extract_data_by_key_list(
        data=dummy_input_data,
        variable_path=dummy_var_path,
        variable_properties=dummy_var_properties,
        called_during_initialization=False,
    )

    assert result == dummy_value
    patch_extract.assert_has_calls([call(dummy_input_data, dummy_var_path), call(dummy_input_data, dummy_var_path)])
    patch_log_missing_data.assert_not_called()


@pytest.mark.parametrize(
    "var_path, var_name, called_during_initialization",
    [
        (["a", "b", "c"], "c", True),
        (["a", "b", 1], "b", True),
        (["a", 2, 0], "a", True),
        (["a", 0, "c"], "c", True),
        (["a", 0, "c", 2], "c", True),
        (["a", "b", "c"], "c", False),
        (["a", "b", 1], "b", False),
        (["a", 2, 0], "a", False),
        (["a", 0, "c"], "c", False),
        (["a", 0, "c", 2], "c", False),
    ],
)
def test_extract_input_data_by_key_list_key_error(
    var_path: List[str | int], var_name: str, called_during_initialization: bool, mocker: MockerFixture
) -> None:
    """Unit tests for making sure data were extracted when error occurs"""
    dummy_input_data: dict[str | int, Any] | list[Any] = {"a": 1, "b": 2}
    dummy_var_properties: dict[str, Any] = {"pattern": r"cow", "minimum_length": 1, "maximum_length": 5}
    patch_extract = mocker.patch.object(DataValidator, "extract_value_by_key_list", side_effect=KeyError)
    patch_log_missing_data = mocker.patch.object(DataValidator, "_log_missing_data")
    dv = DataValidator()

    result = dv._extract_data_by_key_list(
        data=dummy_input_data,
        variable_path=var_path,
        variable_properties=dummy_var_properties,
        called_during_initialization=called_during_initialization,
    )

    assert result is None
    patch_extract.assert_called_once_with(dummy_input_data, var_path)
    patch_log_missing_data.assert_called_once_with(
        variable_properties=dummy_var_properties,
        var_name=var_name,
        called_during_initialization=called_during_initialization,
    )


@pytest.fixture
def cv(mocker: MockerFixture) -> CrossValidator:
    """Fixture to create a CrossValidator with mocked methods."""
    cv = CrossValidator.__new__(CrossValidator)
    mocker.patch.object(cv, "_target_and_save")
    mocker.patch.object(cv, "_evaluate_condition_clause_array")
    mocker.patch.object(cv, "_evaluate_condition")
    return cv


def test_early_exit_when_apply_when_fails_and_eager_true(mocker: MockerFixture, cv: CrossValidator) -> None:
    """Test that cross_validate_data exits early when apply_when fails and eager_termination is True."""
    cross_validation_block = {"apply_when": [{"foo": "bar"}], "rules": [{"r": 1}, {"r": 2}]}
    mock_target_and_save = mocker.patch.object(cv, "_target_and_save")
    mock_evaluate_condition = mocker.patch.object(cv, "_evaluate_condition")
    mock_evaluate_condition_clause_array = mocker.patch.object(
        cv, "_evaluate_condition_clause_array", return_value=False
    )

    result = cv.cross_validate_data({"x": 1}, cross_validation_block, eager_termination=True)

    assert result is True
    mock_target_and_save.assert_called_once_with({"x": 1})
    mock_evaluate_condition_clause_array.assert_called_once_with([{"foo": "bar"}], True)
    mock_evaluate_condition.assert_not_called()


def test_evaluates_all_rules_when_eager_false_and_returns_last(mocker: MockerFixture, cv: CrossValidator) -> None:
    """Test that cross_validate_data evaluates all rules when eager_termination is False and returns last result."""
    mock_evaluate_condition_clause_array = mocker.patch.object(
        cv, "_evaluate_condition_clause_array", return_value=True
    )
    mock_evaluate_condition = mocker.patch.object(cv, "_evaluate_condition", side_effect=[True, False, True])
    rules = [{"r": 1}, {"r": 2}, {"r": 3}]
    cross_validation_block = {"apply_when": [], "rules": rules}

    result = cv.cross_validate_data({"y": 2}, cross_validation_block, eager_termination=False)

    assert result is True
    assert mock_evaluate_condition.call_count == 3
    mock_evaluate_condition.assert_has_calls(
        [mocker.call(rules[0], False), mocker.call(rules[1], False), mocker.call(rules[2], False)]
    )
    mock_evaluate_condition_clause_array.assert_called_once_with([], False)


def test_breaks_on_first_failed_rule_when_eager_true(mocker: MockerFixture, cv: CrossValidator) -> None:
    """Test that cross_validate_data breaks on first failed rule when eager_termination is True."""
    mock_evaluate_condition_clause_array = mocker.patch.object(
        cv, "_evaluate_condition_clause_array", return_value=True
    )
    mock_evaluate_condition = mocker.patch.object(cv, "_evaluate_condition", side_effect=[True, False, True])
    rules = [{"r": 1}, {"r": 2}, {"r": 3}]
    cross_validation_block = {"rules": rules}

    result = cv.cross_validate_data({"z": 3}, cross_validation_block, eager_termination=True)

    assert result is False

    assert mock_evaluate_condition.call_count == 2
    mock_evaluate_condition.assert_has_calls([mocker.call(rules[0], True), mocker.call(rules[1], True)])
    mock_evaluate_condition_clause_array.assert_called_once_with([], True)


@pytest.mark.parametrize(
    "alias_name,value,expected_pool",
    [("test1", 16.4, {"test1": 16.4}), ("test2", 924.6, {"test1": 13, "test2": 924.6})],
)
def test_save_to_alias_pool(alias_name: str, value: Any, expected_pool: dict[str, Any]) -> None:
    """Test the function _save_to_alias_pool()"""
    validator = CrossValidator()
    validator._alias_pool = {"test1": 13}
    validator._save_to_alias_pool(alias_name, value)
    assert validator._alias_pool == expected_pool


@pytest.mark.parametrize(
    "pool,alias,expected",
    [
        ({"a": 1}, "a", 1),
        ({"x": "Y", "z": 3.14}, "x", "Y"),
    ],
)
def test_get_alias_value_returns(pool: dict[str, Any], alias: str, expected: Any) -> None:
    """Test the function _get_alias_value()"""
    v = CrossValidator()
    v._alias_pool = dict(pool)
    assert v._get_alias_value(alias, True, "sum") == expected


@pytest.mark.parametrize("eager_termination", [True, False])
def test_get_alias_value_raises_key_error_when_missing(eager_termination: bool) -> None:
    """Test the function _get_alias_value() when getting unavailable keys names."""
    v = CrossValidator()
    v._alias_pool = {"exists": 10}

    if eager_termination:
        with pytest.raises(ValueError, match=r"Unknown alias name: missing"):
            v._get_alias_value("missing", eager_termination=True, relationship="equal")
        assert len(v._event_logs) == 1
    else:
        result = v._get_alias_value("missing", eager_termination=False, relationship="equal")
        assert result is None
        assert len(v._event_logs) == 1


def test_target_and_save(mocker: MockerFixture) -> None:
    """Test the function target_and_save()"""
    v = CrossValidator()
    mock_save = mocker.patch.object(v, "_save_to_alias_pool")
    v._target_and_save({"a": 1, "b": 1, "c": "value"})

    assert mock_save.call_count == 3


@pytest.mark.parametrize(
    "block",
    [
        ({"variables": {}, "constants": {}}),
        ({"variables": {"x": "A1"}, "constants": {}}),
        ({"variables": {}, "constants": {"k": "K1"}}),
        ({}),
    ],
)
def test_check_target_and_save_block_no_errors(block: dict[str, dict[str, Any]]) -> None:
    """Should not append errors when only allowed keys are present."""
    cv = CrossValidator()
    cv.check_target_and_save_block(block, True)
    assert len(cv._event_logs) == 0


def test_check_target_and_save_block_message_contains_all_invalid_keys() -> None:
    """Sanity check: when multiple invalid keys exist, logs each (not a single aggregated one)."""
    cv = CrossValidator()
    block: dict[str, Any] = {"variables": {}, "constants": {}, "a": {}, "b": {}, "c": {}}

    cv.check_target_and_save_block(block, False)

    assert len(cv._event_logs) == 3
    assert all(any(f"Unsupported keys {k} provided." in e["message"] for e in cv._event_logs) for k in ("a", "b", "c"))


def test_check_target_and_save_block_message_contains_all_invalid_keys_eager_termination() -> None:
    """Sanity check: when multiple invalid keys exist with eager termination."""
    cv = CrossValidator()
    block: dict[str, Any] = {"variables": {}, "constants": {}, "a": {}, "b": {}, "c": {}}

    with pytest.raises(ValueError):
        cv.check_target_and_save_block(block, True)

    assert len(cv._event_logs) == 1


@pytest.mark.parametrize(
    "expression_block, eager_termination",
    [
        ({"operation": "add", "ordered_variables": ["alias_0", "alias_1"], "save_as": "alias_2"}, True),
        ({"operation": "subtract", "ordered_variables": ["alias_0", "alias_1"], "save_as": "alias_2"}, True),
        ({"operation": "multiply", "ordered_variables": ["alias_0", "alias_1"], "save_as": "alias_2"}, True),
        ({"operation": "add", "ordered_variables": ["alias_0", "alias_1"], "save_as": "alias_2"}, False),
        ({"operation": "subtract", "ordered_variables": ["alias_0", "alias_1"], "save_as": "alias_2"}, False),
        ({"operation": "multiply", "ordered_variables": ["alias_0", "alias_1"], "save_as": "alias_2"}, False),
    ],
)
def test_evaluate_expression_unknown_operation(
    expression_block: dict[str, Any], eager_termination: bool, mocker: MockerFixture
) -> None:
    """Unit tests for _evaluate_expression() in CrossValidator"""
    cross_validator = CrossValidator()
    mock_get_alias_value = mocker.patch.object(cross_validator, "_get_alias_value")
    mock_save_to_alias_pool = mocker.patch.object(cross_validator, "_save_to_alias_pool")

    if eager_termination:
        with pytest.raises(ValueError):
            cross_validator._evaluate_expression(expression_block, eager_termination, relationship="equal")
    else:
        result, status = cross_validator._evaluate_expression(expression_block, eager_termination, relationship="equal")
        assert result is None
        assert status is False
    mock_get_alias_value.assert_not_called()
    mock_save_to_alias_pool.assert_not_called()


@pytest.mark.parametrize(
    "expression_block, eager_termination",
    [
        ({"operation": "add", "save_as": "alias_2"}, True),
        ({"operation": "subtract", "save_as": "alias_2"}, True),
        ({"operation": "multiply", "ordered_variables": [], "save_as": "alias_2"}, True),
        ({"operation": "add", "save_as": "alias_2"}, False),
        ({"operation": "subtract", "save_as": "alias_2"}, False),
        ({"operation": "multiply", "save_as": "alias_2"}, False),
    ],
)
def test_evaluate_expression_no_ordered_variables(
    expression_block: dict[str, Any], eager_termination: bool, mocker: MockerFixture
) -> None:
    """Test the behavior of _evaluate_expression when ordered_variables is missing or empty."""
    cross_validator = CrossValidator()
    mock_get_alias_value = mocker.patch.object(cross_validator, "_get_alias_value")
    mock_save_to_alias_pool = mocker.patch.object(cross_validator, "_save_to_alias_pool")

    if eager_termination:
        with pytest.raises(ValueError):
            cross_validator._evaluate_expression(expression_block, eager_termination, relationship="equal")
    else:
        result, status = cross_validator._evaluate_expression(expression_block, eager_termination, relationship="equal")
        assert result is None
        assert status is False
    mock_get_alias_value.assert_not_called()
    mock_save_to_alias_pool.assert_not_called()


@pytest.mark.parametrize(
    "expression_block, selected_variables, eager_termination",
    [
        ({"operation": "sum", "ordered_variables": ["alias_0", "alias_1"], "apply_to": "group"}, [[], []], True),
        ({"operation": "difference", "ordered_variables": ["alias_0", "alias_1"], "apply_to": "group"}, [{}, {}], True),
        (
            {"operation": "average", "ordered_variables": ["alias_0", "alias_1"], "apply_to": "group"},
            [[1, 2, 3], {"a": 1, "b": 2}],
            True,
        ),
        (
            {"operation": "product", "ordered_variables": ["alias_0", "alias_1"], "apply_to": "group"},
            [[4, 5, 6], ["a", "b", "c"]],
            False,
        ),
        (
            {"operation": "division", "ordered_variables": ["alias_0", "alias_1"], "apply_to": "group"},
            [{"a": [], "b": []}, [{}, {}]],
            False,
        ),
        ({"operation": "no_op", "ordered_variables": ["alias_0", "alias_1"], "apply_to": "group"}, [[{}], []], False),
    ],
)
def test_validate_expression_block_with_complex_variable_values_multiple_complex_variable(
    expression_block: dict[str, Any], selected_variables: list[Any], eager_termination: bool
) -> None:
    """
    Unit tests for _validate_expression_block_with_complex_variable_values() in CrossValidator when
    multiple complex variables are selected
    """
    cross_validator = CrossValidator()

    if eager_termination:
        with pytest.raises(ValueError):
            cross_validator._validate_expression_block_with_complex_variable_values(
                expression_block, selected_variables, eager_termination
            )
    else:
        result = cross_validator._validate_expression_block_with_complex_variable_values(
            expression_block, selected_variables, eager_termination
        )
        assert result is False


@pytest.mark.parametrize(
    "expression_block, selected_variables, eager_termination",
    [
        ({"operation": "sum", "ordered_variables": ["alias_0"]}, [[]], True),
        ({"operation": "difference", "ordered_variables": ["alias_0"]}, [{}], True),
        ({"operation": "average", "ordered_variables": ["alias_0"]}, [[1, 2, 3]], True),
        ({"operation": "product", "ordered_variables": ["alias_0"]}, [{"a": 1, "b": 2, "c": 3}], False),
        ({"operation": "division", "ordered_variables": ["alias_0"]}, [{"a": [], "b": []}], False),
        ({"operation": "no_op", "ordered_variables": ["alias_0"]}, [[{}]], False),
    ],
)
def test_validate_expression_block_with_complex_variable_values_no_apply_to(
    expression_block: dict[str, Any], selected_variables: list[Any], eager_termination: bool, mocker: MockerFixture
) -> None:
    """
    Unit tests for _validate_expression_block_with_complex_variable_values() in CrossValidator
    when a complex variable is selected and the `apply_to` key is missing.
    """
    cross_validator = CrossValidator()

    if eager_termination:
        with pytest.raises(ValueError):
            cross_validator._validate_expression_block_with_complex_variable_values(
                expression_block, selected_variables, eager_termination
            )
    else:
        result = cross_validator._validate_expression_block_with_complex_variable_values(
            expression_block, selected_variables, eager_termination
        )
        assert result is False


@pytest.mark.parametrize(
    "expression_block, selected_variables, eager_termination",
    [
        ({"operation": "sum", "ordered_variables": ["alias_0"], "apply_to": "unknown"}, [[]], True),
        ({"operation": "sum", "ordered_variables": ["alias_0"], "apply_to": "unknown"}, [[]], False),
    ],
)
def test_validate_expression_block_with_complex_variable_values_unknown_apply_to_value(
    expression_block: dict[str, Any], selected_variables: list[Any], eager_termination: bool, mocker: MockerFixture
) -> None:
    """
    Unit tests for _validate_expression_block_with_complex_variable_values() in CrossValidator
    when a complex variable is selected and the `apply_to` key is set to an unknown value.
    """
    cross_validator = CrossValidator()

    if eager_termination:
        with pytest.raises(ValueError):
            cross_validator._validate_expression_block_with_complex_variable_values(
                expression_block, selected_variables, eager_termination
            )
    else:
        result = cross_validator._validate_expression_block_with_complex_variable_values(
            expression_block, selected_variables, eager_termination
        )
        assert result is False


@pytest.mark.parametrize(
    "expression_block, selected_variables, expected_result",
    [
        ({"operation": "no_op", "ordered_variables": ["alias_0"], "apply_to": "individual"}, [[1, 2, 3]], [1, 2, 3]),
        ({"operation": "no_op", "ordered_variables": ["alias_0"], "apply_to": "individual"}, [[]], []),
        (
            {"operation": "no_op", "ordered_variables": ["alias_0"], "apply_to": "individual", "save_as": "abc"},
            [{"a": 1, "b": 2, "c": 3}],
            [1, 2, 3],
        ),
        ({"operation": "no_op", "ordered_variables": ["alias_0"], "apply_to": "individual"}, [{}], []),
        (
            {"operation": "no_op", "ordered_variables": ["alias_0"], "apply_to": "individual", "save_as": "def"},
            [{"a": [], "b": []}],
            [[], []],
        ),
        (
            {"operation": "no_op", "ordered_variables": ["alias_0"], "apply_to": "individual"},
            [[{}, {}, {}]],
            [{}, {}, {}],
        ),
    ],
)
def test_evaluate_expression_apply_to_individual(
    expression_block: dict[str, Any], selected_variables: list[Any], expected_result: Any, mocker: MockerFixture
) -> None:
    """
    Unit tests for _evaluate_expression() in CrossValidator when a complex variable is selected
    and `apply_to` is set to `individual`
    """
    cross_validator = CrossValidator()
    mock_get_alias_value = mocker.patch.object(cross_validator, "_get_alias_value", side_effect=selected_variables)
    mock_save_to_alias_pool = mocker.patch.object(cross_validator, "_save_to_alias_pool")

    result, status = cross_validator._evaluate_expression(expression_block, False, relationship="equal")
    assert result == expected_result
    assert status is True
    mock_get_alias_value.assert_called_once()
    if "save_as" in expression_block:
        mock_save_to_alias_pool.assert_called_once_with(alias_name=expression_block["save_as"], value=result)
    else:
        mock_save_to_alias_pool.assert_not_called()


@pytest.mark.parametrize(
    "expression_block, selected_variables, expected_result",
    [
        ({"operation": "sum", "ordered_variables": ["alias_0"], "apply_to": "group"}, [[1, 2, 3]], [6]),
        ({"operation": "difference", "ordered_variables": ["alias_0"], "apply_to": "group"}, [[]], [None]),
        (
            {"operation": "product", "ordered_variables": ["alias_0"], "apply_to": "group", "save_as": "abc"},
            [{"a": 1, "b": 2, "c": 3}],
            [6],
        ),
        ({"operation": "division", "ordered_variables": ["alias_0"], "apply_to": "group"}, [{}], [None]),
        ({"operation": "no_op", "ordered_variables": ["a", "b", "c"], "save_as": "def"}, [2, 5, 8], [2, 5, 8]),
        (
            {"operation": "average", "ordered_variables": ["a", "b", "c", "d", "e", "f", "g", "h"]},
            [8, 7, 6, 5, 4, 3, 2, 1],
            [4.5],
        ),
    ],
)
def test_evaluate_expression_apply_to_group(
    expression_block: dict[str, Any], selected_variables: list[Any], expected_result: Any, mocker: MockerFixture
) -> None:
    cross_validator = CrossValidator()
    mocker.patch.object(cross_validator, "_get_alias_value", side_effect=selected_variables)
    mock_save_to_alias_pool = mocker.patch.object(cross_validator, "_save_to_alias_pool")

    result, status = cross_validator._evaluate_expression(expression_block, False, relationship="equal")
    assert result == expected_result
    assert status is True
    if "save_as" in expression_block:
        mock_save_to_alias_pool.assert_called_once_with(alias_name=expression_block["save_as"], value=result)
    else:
        mock_save_to_alias_pool.assert_not_called()


@pytest.mark.parametrize(
    "relationship",
    ["equal", "greater", "greater_or_equal_to", "not_equal", "is_of_type", "regex"],
)
@pytest.mark.parametrize("eager_termination", [True, False])
def test_validate_relationship_valid_values(relationship: str, eager_termination: bool) -> None:
    """Valid relationship strings should pass with no event logs."""
    cv = CrossValidator()

    # Act
    result = cv._validate_relationship(relationship, eager_termination)

    # Assert
    assert result is True
    assert len(cv._event_logs) == 0


@pytest.mark.parametrize("eager_termination", [True, False])
def test_validate_relationship_non_string(eager_termination: bool) -> None:
    """Non-string relationship should log error; optionally raise in eager mode."""
    cv = CrossValidator()

    if eager_termination:
        with pytest.raises(ValueError, match=r"Relationship must be a string\."):
            cv._validate_relationship(123, eager_termination=True)
        assert len(cv._event_logs) == 1
    else:
        # Act
        ok = cv._validate_relationship(123, eager_termination=False)
        # Assert
        assert ok is False
        assert len(cv._event_logs) == 1


@pytest.mark.parametrize("eager_termination", [True, False])
def test_validate_relationship_invalid_value(eager_termination: bool) -> None:
    """Unknown relationship should log error; optionally raise in eager mode."""
    cv = CrossValidator()

    if eager_termination:
        with pytest.raises(ValueError, match=r"Invalid relationship provided\."):
            cv._validate_relationship("something_else", eager_termination=True)
        assert len(cv._event_logs) == 1
    else:
        ok = cv._validate_relationship("something_else", eager_termination=False)
        assert ok is False
        assert len(cv._event_logs) == 1


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (1, 1, True),
        (1, 2, False),
        ("x", "x", True),
        ("x", "y", False),
        (True, True, True),
        (True, False, False),
    ],
)
def test_evaluate_equal_condition(a: Any, b: Any, expected: bool) -> None:
    """_evaluate_equal_condition returns Python == semantics."""
    cv = CrossValidator()
    assert cv._evaluate_equal_condition(a, b) is expected


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (2, 1, True),
        (1, 2, False),
        ("b", "a", True),
        ("a", "b", False),
    ],
)
def test_evaluate_greater_condition(a: Any, b: Any, expected: bool) -> None:
    """_evaluate_greater_condition returns Python > semantics."""
    cv = CrossValidator()
    assert cv._evaluate_greater_condition(a, b) is expected


@pytest.mark.parametrize(
    "value,expected",
    [
        ([None], True),
        ([0], False),
        ([[""]], False),
        ([[]], False),
    ],
)
def test_evaluate_is_null(value: Any, expected: bool) -> None:
    """_evaluate_is_null checks identity to None."""
    cv = CrossValidator()
    assert cv._evaluate_is_null(value) is expected


@pytest.mark.parametrize(
    "data_type,left_value,expected",
    [
        (["string"], ["abc"], True),
        (["string"], [123], False),
        (["integer"], [7], True),
        (["integer"], [True], False),
        (["float"], [1.2], True),
        (["float"], [7], False),
        (["boolean"], [True], True),
        (["boolean"], [0], False),
        (["number"], [7], True),
        (["number"], [1.2], True),
        (["number"], [False], False),
        (["string"], ["ok"], True),
    ],
)
@pytest.mark.parametrize("eager_termination", [True, False])
def test_evaluate_is_type_supported_types(
    data_type: str, left_value: Any, expected: bool, eager_termination: bool
) -> None:
    """Supported types honor bool/int nuances and case-insensitive type strings."""
    cv = CrossValidator()
    assert cv._evaluate_is_type(left_value, data_type, eager_termination) is expected
    # No error logs on supported types
    assert all(e["error"] != "Invalid data type expectation." for e in cv._event_logs)


@pytest.mark.parametrize("eager_termination", [True, False])
def test_evaluate_is_type_data_type_not_str(eager_termination: bool) -> None:
    """Non-string data_type logs and optionally raises."""
    cv = CrossValidator()
    if eager_termination:
        with pytest.raises(ValueError, match=r"Invalid type comparison in cross validation\."):
            cv._evaluate_is_type(["x"], [123], eager_termination=True)
        assert len(cv._event_logs) == 1
    else:
        valid = cv._evaluate_is_type(["x"], [123], eager_termination=False)
        assert not valid
        assert len(cv._event_logs) == 1


@pytest.mark.parametrize("eager_termination", [True, False])
def test_evaluate_is_type_unsupported_type_string(eager_termination: bool) -> None:
    """Unsupported type string logs and optionally raises."""
    cv = CrossValidator()
    if eager_termination:
        with pytest.raises(ValueError, match=r"Unsupported data type weird\. Supported types:"):
            cv._evaluate_is_type(["x"], ["weird"], eager_termination=True)
        assert len(cv._event_logs) == 1
    else:
        valid = cv._evaluate_is_type(["x"], ["weird"], eager_termination=False)
        assert not valid
        assert len(cv._event_logs) == 1


@pytest.mark.parametrize(
    "text,pattern,expected",
    [
        ("abc", r"a.c", True),
        ("abc", r"^a.*c$", True),
        ("abc", r"^ab$", False),
        ("", r"^$", True),
    ],
)
def test_evaluate_regex_fullmatch(text: str, pattern: str, expected: bool) -> None:
    """
    Per docstring: left_hand_value is the string, right_hand_value is the regex pattern.
    NOTE: If this test fails, check that _evaluate_regex calls re.fullmatch(pattern, text).
    """
    cv = CrossValidator()
    assert cv._evaluate_regex(text, pattern) is expected


@pytest.mark.parametrize("eager_termination", [True, False])
def test_evaluate_condition_short_circuits_when_validation_fails(
    mocker: MockerFixture, eager_termination: bool
) -> None:
    """If _validate_condition_clause returns False, no expressions are evaluated and result is False."""
    cv = CrossValidator()
    mocker.patch.object(cv, "_validate_condition_clause", return_value=False)
    mock_eval = mocker.patch.object(cv, "_evaluate_expression")

    valid = cv._evaluate_condition({"relationship": "equal"}, eager_termination)

    assert not valid
    mock_eval.assert_not_called()


@pytest.mark.parametrize("eager_termination", [True, False])
def test_evaluate_condition_returns_false_when_side_not_evaluated(
    mocker: MockerFixture, eager_termination: bool
) -> None:
    """If either side doesn't evaluate, the condition returns False."""
    cv = CrossValidator()
    mocker.patch.object(cv, "_validate_condition_clause", return_value=True)
    # Left evaluated False; right True
    mocker.patch.object(cv, "_evaluate_expression", side_effect=[("L", False), ("R", True)])

    valid = cv._evaluate_condition({"relationship": "equal", "left_hand": {}, "right_hand": {}}, eager_termination)

    assert not valid


@pytest.mark.parametrize("eager_termination", [True, False])
def test_evaluate_condition_equal_path(mocker: MockerFixture, eager_termination: bool) -> None:
    """Dispatch to _evaluate_equal_condition for 'equal'."""
    cv = CrossValidator()
    mocker.patch.object(cv, "_validate_condition_clause", return_value=True)
    mocker.patch.object(cv, "_evaluate_expression", side_effect=[("A", True), ("B", True)])
    mock_eq = mocker.patch.object(cv, "_evaluate_equal_condition", return_value=True)

    valid = cv._evaluate_condition({"relationship": "equal", "left_hand": {}, "right_hand": {}}, eager_termination)

    assert valid
    mock_eq.assert_called_once_with("A", "B")


@pytest.mark.parametrize("eager_termination", [True, False])
def test_evaluate_condition_greater_or_equal_short_circuit(mocker: MockerFixture, eager_termination: bool) -> None:
    """When 'greater_or_equal_to', greater=True should short-circuit (no equality call)."""
    cv = CrossValidator()
    mocker.patch.object(cv, "_validate_condition_clause", return_value=True)
    mocker.patch.object(cv, "_evaluate_expression", side_effect=[(5, True), (2, True)])
    mock_gt = mocker.patch.object(cv, "_evaluate_greater_condition", return_value=True)
    mock_eq = mocker.patch.object(cv, "_evaluate_equal_condition", return_value=False)

    valid = cv._evaluate_condition(
        {"relationship": "greater_or_equal_to", "left_hand": {}, "right_hand": {}}, eager_termination
    )

    assert valid
    mock_gt.assert_called_once_with(5, 2)
    mock_eq.assert_not_called()


@pytest.mark.parametrize("eager_termination", [True, False])
def test_evaluate_condition_greater_or_equal_falls_back_to_equal(
    mocker: MockerFixture, eager_termination: bool
) -> None:
    """When 'greater_or_equal_to', if greater=False, equality result is used."""
    cv = CrossValidator()
    mocker.patch.object(cv, "_validate_condition_clause", return_value=True)
    mocker.patch.object(cv, "_evaluate_expression", side_effect=[(2, True), (2, True)])
    mock_gt = mocker.patch.object(cv, "_evaluate_greater_condition", return_value=False)
    mock_eq = mocker.patch.object(cv, "_evaluate_equal_condition", return_value=True)

    valid = cv._evaluate_condition(
        {"relationship": "greater_or_equal_to", "left_hand": {}, "right_hand": {}}, eager_termination
    )

    assert valid
    mock_gt.assert_called_once_with(2, 2)
    mock_eq.assert_called_once_with(2, 2)


@pytest.mark.parametrize("eager_termination", [True, False])
def test_evaluate_condition_not_equal_inverts_equality(mocker: MockerFixture, eager_termination: bool) -> None:
    """'not_equal' returns logical inversion of equality."""
    cv = CrossValidator()
    mocker.patch.object(cv, "_validate_condition_clause", return_value=True)
    mocker.patch.object(cv, "_evaluate_expression", side_effect=[("foo", True), ("bar", True)])
    mock_eq = mocker.patch.object(cv, "_evaluate_equal_condition", return_value=False)

    valid = cv._evaluate_condition({"relationship": "not_equal", "left_hand": {}, "right_hand": {}}, eager_termination)

    assert valid
    mock_eq.assert_called_once_with("foo", "bar")


@pytest.mark.parametrize("eager_termination", [True, False])
def test_evaluate_condition_is_of_type_passes_eager(mocker: MockerFixture, eager_termination: bool) -> None:
    """'is_of_type' should pass eager flag to _evaluate_is_type."""
    cv = CrossValidator()
    mocker.patch.object(cv, "_validate_condition_clause", return_value=True)
    mocker.patch.object(cv, "_evaluate_expression", side_effect=[("text", True), ("string", True)])
    mock_is_type = mocker.patch.object(cv, "_evaluate_is_type", return_value=True)

    valid = cv._evaluate_condition({"relationship": "is_of_type", "left_hand": {}, "right_hand": {}}, eager_termination)

    assert valid
    mock_is_type.assert_called_once_with("text", "string", eager_termination)


@pytest.mark.parametrize("eager_termination", [True, False])
def test_evaluate_condition_is_null_branch(mocker: MockerFixture, eager_termination: bool) -> None:
    """'is_null' should evaluate only semantics of left-hand (we still provide right to enter branch)."""
    cv = CrossValidator()
    mocker.patch.object(cv, "_validate_condition_clause", return_value=True)
    # Both evaluated True so the code enters the relationship switch
    mocker.patch.object(cv, "_evaluate_expression", side_effect=[(None, True), ("ignored", True)])
    mock_is_null = mocker.patch.object(cv, "_evaluate_is_null", return_value=True)

    valid = cv._evaluate_condition({"relationship": "is_null", "left_hand": {}, "right_hand": {}}, eager_termination)

    assert valid
    mock_is_null.assert_called_once_with(None)


@pytest.mark.parametrize("eager_termination", [True, False])
def test_evaluate_condition_regex_branch(mocker: MockerFixture, eager_termination: bool) -> None:
    """Fallback (else) is regex."""
    cv = CrossValidator()
    mocker.patch.object(cv, "_validate_condition_clause", return_value=True)
    mocker.patch.object(cv, "_evaluate_expression", side_effect=[("abc", True), (r"a.c", True)])
    mock_regex = mocker.patch.object(cv, "_evaluate_regex", return_value=True)

    ok = cv._evaluate_condition({"relationship": "regex", "left_hand": {}, "right_hand": {}}, eager_termination)

    assert ok is True
    mock_regex.assert_called_once_with("abc", r"a.c")


@pytest.mark.parametrize("eager_termination", [True, False])
def test_evaluate_condition_clause_array_all_true(mocker: MockerFixture, eager_termination: bool) -> None:
    """Array evaluation returns True when all clauses pass."""
    cv = CrossValidator()
    mock = mocker.patch.object(cv, "_evaluate_condition", side_effect=[True, True, True])

    valid = cv._evaluate_condition_clause_array([{}, {}, {}], eager_termination)

    assert valid
    assert mock.call_count == 3


def test_validate_condition_clause_ok(mocker: MockerFixture) -> None:
    """True when relationship valid and both sides present."""
    v = CrossValidator()
    mocker.patch.object(v, "_validate_relationship", return_value=True)
    log = mocker.patch.object(v, "_log_missing_condition_clause_field")
    clause = {"left_hand": 1, "right_hand": 2, "relationship": "equal"}
    result = v._validate_condition_clause(clause, eager_termination=False)
    assert result is True
    log.assert_not_called()


def test_validate_condition_clause_missing_both_no_eager(mocker: MockerFixture) -> None:
    """False and logs both fields when not eager."""
    v = CrossValidator()
    mocker.patch.object(v, "_validate_relationship", return_value=True)
    log = mocker.patch.object(v, "_log_missing_condition_clause_field")
    clause = {"relationship": "equal"}
    result = v._validate_condition_clause(clause, eager_termination=False)
    assert result is False
    assert log.call_args_list == [call("left hand"), call("right hand")]


def test_validate_condition_clause_missing_left_no_eager(mocker: MockerFixture) -> None:
    """False and logs left when not eager."""
    v = CrossValidator()
    mocker.patch.object(v, "_validate_relationship", return_value=True)
    log = mocker.patch.object(v, "_log_missing_condition_clause_field")
    clause = {"right_hand": 2, "relationship": "equal"}
    result = v._validate_condition_clause(clause, eager_termination=False)
    assert result is False
    assert log.call_args_list == [call("left hand")]


def test_validate_condition_clause_missing_right_no_eager(mocker: MockerFixture) -> None:
    """False and logs right when not eager."""
    v = CrossValidator()
    mocker.patch.object(v, "_validate_relationship", return_value=True)
    log = mocker.patch.object(v, "_log_missing_condition_clause_field")
    clause = {"left_hand": 1, "relationship": "equal"}
    result = v._validate_condition_clause(clause, eager_termination=False)
    assert result is False
    assert log.call_args_list == [call("right hand")]


def test_validate_condition_clause_missing_both_eager_raises(mocker: MockerFixture) -> None:
    """Raises KeyError and logs both when eager."""
    v = CrossValidator()
    mocker.patch.object(v, "_validate_relationship", return_value=True)
    log = mocker.patch.object(v, "_log_missing_condition_clause_field")
    clause = {"relationship": "equal"}
    with pytest.raises(KeyError):
        v._validate_condition_clause(clause, eager_termination=True)
    assert log.call_args_list == [call("left hand"), call("right hand")]


def test_validate_condition_clause_invalid_relationship(mocker: MockerFixture) -> None:
    """False when relationship validation fails."""
    v = CrossValidator()
    mocker.patch.object(v, "_validate_relationship", return_value=False)
    log = mocker.patch.object(v, "_log_missing_condition_clause_field")
    clause = {"left_hand": 1, "right_hand": 2, "relationship": "bogus"}
    result = v._validate_condition_clause(clause, eager_termination=False)
    assert result is False
    log.assert_not_called()


def test_log_missing_condition_clause_field_only() -> None:
    """Appends one correctly shaped entry."""
    v = CrossValidator()
    v._event_logs = []
    v._log_missing_condition_clause_field("left hand")
    assert len(v._event_logs) == 1
    e = v._event_logs[0]
    assert e["error"] == "Missing required condition clause field"
    assert e["message"] == "Missing the left hand field in condition clause."

from functools import reduce
from typing import Dict, Any, List, Union, Optional, Type

import pytest
from mock.mock import call
from pytest_mock import MockerFixture

from RUFAS.elements import ElementsCounter, ElementState
from RUFAS.input_validator import InputValidator
from RUFAS.output_manager import OutputManager


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


@pytest.mark.parametrize(
    "dummy_variable_properties, dummy_element_hierarchy, expected_result, expected_warning_call_count",
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
            0,
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
            0,
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
            0,
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
            0,
        ),
    ],
)
def test_fix_string_type_critical_data(
    dummy_variable_properties: dict[str, Any],
    dummy_element_hierarchy: list[str],
    expected_result: bool,
    expected_warning_call_count: int,
    mocker: MockerFixture
) -> None:
    """Unit test for critical string-type data for _fix_data function in file input_manager.py"""

    dummy_input_data = mock_input_string_data_for_fix_data()
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
    "dummy_variable_properties, dummy_element_hierarchy, expected_value, expected_result, expected_warning_call_count",
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
            2,
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
            2,
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
            2,
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
            2,
        ),
    ],
)
def test_fix_number_type_fixable_data(
    dummy_variable_properties: dict[str, Any],
    dummy_element_hierarchy: list[str],
    expected_value: str,
    expected_result: bool,
    expected_warning_call_count: int,
    mocker: MockerFixture,
) -> None:
    """Unit test for fixable number-type data for _fix_data function in file input_manager.py"""

    dummy_input_data = mock_input_number_data_for_fix_data()
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
    "dummy_variable_properties, dummy_element_hierarchy, expected_result, " "expected_warning_call_count",
    [
        (
            {
                "type": "number",
                "minimum": 0,
                "maximum": 10,
            },
            ["element6"],
            False,
            0,
        ),
        (
            {
                "type": "number",
                "minimum": 0,
                "maximum": 10,
            },
            ["element7"],
            False,
            0,
        ),
        (
            {
                "type": "number",
                "minimum": 1,
                "maximum": 10,
            },
            ["element8"],
            False,
            0,
        ),
        (
            {
                "type": "number",
                "minimum": 0,
                "maximum": 10,
            },
            ["element9", "element10"],
            False,
            0,
        ),
    ],
)
def test_fix_number_type_critical_data(
    dummy_variable_properties: dict[str, Any],
    dummy_element_hierarchy: list[str],
    expected_result: bool,
    expected_warning_call_count: int,
    mocker: MockerFixture
) -> None:
    """Unit test for critical number-type data for _fix_data function in file input_manager.py"""

    dummy_input_data = mock_input_number_data_for_fix_data()
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
    input_data: Union[List[Any], Dict[str, Any]],
    variable_path: List[Union[str, int]],
    expected: Optional[Any],
    expected_exception: Optional[Type[Exception]],
) -> None:
    """
    Unit test for the _extract_value_by_key_list() method of the InputManager class.
    """
    # Act and assert
    if expected_exception:
        with pytest.raises(expected_exception):
            InputValidator.extract_value_by_key_list(input_data, variable_path)
    else:
        result = InputValidator.extract_value_by_key_list(input_data, variable_path)
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

    # Act
    result = InputValidator.convert_variable_path_to_str(variable_path)

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
    variable_path: List[Union[str, int]],
    variable_properties: Dict[str, Any],
    input_data: Dict[str, Any],
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
    mocker.patch.object(InputValidator, "_extract_input_data_by_key_list", return_value=patch_extract_return)
    mocker.patch.object(InputValidator, "validate_input_by_type", return_value=patch_validate_return)
    mocker.patch("RUFAS.input_manager.om.add_warning", return_value=None)
    mock_elements_counter = mocker.MagicMock()

    # Act
    result = InputValidator._object_type_validator(
        variable_path,
        variable_properties,
        input_data,
        eager_termination,
        properties_blob_key,
        mock_elements_counter,
        True,
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
    mocker.patch.object(InputValidator, "_extract_input_data_by_key_list", return_value=data)
    mocker.patch.object(InputValidator, "validate_input_by_type", return_value=True)
    mocker.patch.object(InputValidator, "convert_variable_path_to_str", return_value="dummy path")
    add_warning = mocker.patch("RUFAS.input_manager.om.add_warning", return_value=None)
    mock_elements_counter = mocker.MagicMock()
    variable_properties: dict[str, Any] = {"key1": {}, "key2": {}}
    violation_msg = "Violates properties defined in metadata properties section 'properties blob'."
    info_map = {"class": "InputValidator", "function": "_object_type_validator"}
    expected_add_warning_calls = [
        mocker.call(
            "Validation: object contains extraneous data",
            f"Variable: 'dummy path' contains data at key '{key}' that is not specified in the metadata properties. "
            f"{violation_msg}",
            info_map,
        )
        for key in removed_keys
    ]

    result = InputValidator._object_type_validator(
        ["path", "to", "var"],
        variable_properties,
        {"dummy": "data"},
        False,
        "properties blob",
        mock_elements_counter,
        True,
    )

    assert result is True
    add_warning.assert_has_calls(expected_add_warning_calls)


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

    # Arrange
    patch_for_add_warning = mocker.patch("RUFAS.input_manager.om.add_warning")

    # Act
    result = InputValidator._validate_array_container_properties(
        variable_path, variable_properties, input_data, properties_blob_key
    )

    # Assert
    assert result == expected_result
    if expected_warning:
        patch_for_add_warning.assert_called_with(
            expected_warning,
            mocker.ANY,
            mocker.ANY,
        )
    else:
        patch_for_add_warning.assert_not_called()


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
    variable_path: List[Union[str, int]],
    variable_properties: Dict[str, Any],
    input_data: Dict[str, Any],
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
    mocker.patch.object(InputValidator, "_extract_input_data_by_key_list", return_value=patch_extract_return)
    mocker.patch.object(InputValidator, "_validate_array_container_properties", return_value=patch_container_valid)
    mocker.patch.object(InputValidator, "validate_input_by_type", return_value=patch_element_valid)
    mock_elements_counter = mocker.MagicMock()

    # Act
    result = InputValidator._array_type_validator(
        variable_path,
        variable_properties,
        input_data,
        eager_termination,
        properties_blob_key,
        mock_elements_counter,
        True,
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
    input_data = {"path": {"to": {"variable": input_value}}}
    eager_termination = False
    properties_blob_key = "blobKey"
    elements_counter = mocker.MagicMock()

    mocker.patch.object(InputValidator, "extract_value_by_key_list", return_value=input_value)
    mocker.patch.object(InputValidator, "convert_variable_path_to_str", return_value="path.to.variable")
    patch_for_fix_data = mocker.patch.object(InputValidator, "_fix_data", return_value=fixable)

    validator_mock = mocker.patch.object(InputValidator, f"_{data_type}_type_validator", return_value=validator_return)

    # Act
    result = InputValidator.validate_input_by_type(
        variable_properties, variable_path, input_data, eager_termination, properties_blob_key, elements_counter, True
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
    variable_path = ["valid_key"]
    properties_blob_key = "dummy_properties_blob_key"
    input_data = {"valid_key": {"another_valid_key": "value"}}
    eager_termination = False
    elements_counter = ElementsCounter()

    # Act and Assert
    with pytest.raises(KeyError):
        InputValidator.validate_input_by_type(
            variable_properties,
            variable_path,
            input_data,
            eager_termination,
            properties_blob_key,
            elements_counter,
            True,
        )


@pytest.mark.parametrize(
    "does_file_exist, metadata, expected_exception",
    [
        (
            True,
            {"files": {
                "file1": {"path": "valid/path/to/file1.csv", "type": "csv", "properties": "some properties"}}},
            False,
        ),
        (
            False,
            {"files": {
                "file1": {"path": "valid/path/to/file1.json", "type": "json", "properties": "some properties"}}},
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
                        "path": "valid/path/to/file1.json",
                        "type": "json",
                        "properties": "",
                    }
                }
            },
            True,
        ),
    ],
)
def test_validate_metadata(
    mocker: MockerFixture,
    does_file_exist: bool,
    metadata: Dict[str, Any],
    expected_exception: bool,
) -> None:
    mocker.patch("os.path.isfile", return_value=does_file_exist)
    mock_add_error = mocker.patch("RUFAS.output_manager.OutputManager.add_error")
    mock_add_log = mocker.patch("RUFAS.output_manager.OutputManager.add_log")

    if expected_exception:
        with pytest.raises(ValueError):
            InputValidator.validate_metadata(metadata)
        mock_add_log.assert_not_called()
        mock_add_error.assert_called()
    else:
        InputValidator.validate_metadata(metadata)
        mock_add_log.assert_called()
        mock_add_error.assert_not_called()


@pytest.mark.parametrize(
    "metadata, limit, expected_depth, expected_path, should_raise, expected_errors, expected_err_msg",
    [
        ({"properties": {"a": {"type": "number"}}}, 2, 1, ["a"], False, [], ""),
        (
            {"properties": {"a": {"b": {"type": "array", "properties": {}}}}},
            3,
            3,
            ["a", "b", "properties"],
            False,
            [],
            "",
        ),
        (
            {"properties": {"a": {"b": {"c": {"type": "bool"}}}}},
            2,
            3,
            ["a", "b", "c"],
            True,
            ["Max metadata depth exceeded."],
            "Metadata depth exceeds maximum allowed depth of 2 at path ['a', 'b', 'c']",
        ),
        ({"properties": {"a": {"b": {"c": {"type": "string"}}}}}, 3, 3, ["a", "b", "c"], False, [], ""),
        (
            {"properties": {"a": {"b": {"type": "invalid_type"}}}},
            3,
            2,
            ["a", "b"],
            True,
            ["Properties value type error"],
            "Properties 'type' value not in ['number', 'array', 'bool', 'string', 'object']",
        ),
        (
            {"properties": {"a": {"b": {"c": {"type": "object", "unique_key": "yes"}}}}},
            3,
            3,
            ["a", "b", "c"],
            False,
            [],
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
    expected_errors: List[str],
    expected_err_msg: str,
) -> None:
    """Tests _validate_properties() function in InputManager."""
    # Initiated to avoid the call of add_log in __init__ to be recorded
    om = OutputManager()  # noqa

    mock_add_error = mocker.patch("RUFAS.output_manager.OutputManager.add_error")
    mock_add_log = mocker.patch("RUFAS.output_manager.OutputManager.add_log")

    if should_raise:
        with pytest.raises(ValueError) as exc_info:
            InputValidator.validate_properties(metadata, limit)
        assert str(exc_info.value) == expected_err_msg
        assert mock_add_error.call_count == len(expected_errors)
        for error_msg in expected_errors:
            mock_add_error.assert_any_call(error_msg, mocker.ANY, mocker.ANY)
        mock_add_log.assert_not_called()
    else:
        InputValidator.validate_properties(metadata, limit)
        mock_add_log.assert_called()
        mock_add_error.assert_not_called()
        assert mock_add_log.call_args_list == [
            call(
                "Metadata properties depth",
                f"Max depth of metadata properties is {expected_depth}",
                {"class": "InputValidator", "function": "validate_properties"},
            ),
            call(
                "Metadata properties path",
                f"Deepest path of metadata properties is {expected_path}",
                {"class": "InputValidator", "function": "validate_properties"},
            ),
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
    mock_add_error = mocker.patch("RUFAS.output_manager.OutputManager.add_error")
    mock_validate_properties_keys = mocker.patch(
        "RUFAS.input_validator.InputValidator._validate_metadata_properties_keys")
    info_map = {"class": "InputValidator", "function": "_metadata_number_validator"}
    if should_raise:
        with pytest.raises(ValueError):
            InputValidator._metadata_number_validator(key_path, value)
        assert mock_add_error.called
        assert mock_add_error.call_args[0] == (error_title, error_msg, info_map)
        mock_validate_properties_keys.assert_called_once()
    else:
        InputValidator._metadata_number_validator(key_path, value)
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
    mock_add_error = mocker.patch("RUFAS.output_manager.OutputManager.add_error")
    mock_validate_properties_keys = mocker.patch(
        "RUFAS.input_validator.InputValidator._validate_metadata_properties_keys")
    info_map = {"class": "InputValidator", "function": "_metadata_string_validator"}

    if should_raise:
        with pytest.raises(ValueError):
            InputValidator._metadata_string_validator(key_path, value)
        assert mock_add_error.called
        assert mock_add_error.call_args[0] == (error_title, error_msg, info_map)
        mock_validate_properties_keys.assert_called_once()
    else:
        InputValidator._metadata_string_validator(key_path, value)
        mock_add_error.assert_not_called()
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
    mock_add_error = mocker.patch("RUFAS.output_manager.OutputManager.add_error")
    mock_validate_properties_keys = mocker.patch(
        "RUFAS.input_validator.InputValidator._validate_metadata_properties_keys")
    info_map = {"class": "InputValidator", "function": "_metadata_bool_validator"}

    if should_raise:
        with pytest.raises(ValueError):
            InputValidator._metadata_bool_validator(key_path, value)
        assert mock_add_error.called
        assert mock_add_error.call_args[0] == (error_title, error_msg, info_map)
        mock_validate_properties_keys.assert_called_once()
    else:
        InputValidator._metadata_bool_validator(key_path, value)
        mock_add_error.assert_not_called()
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
    mock_add_error = mocker.patch("RUFAS.output_manager.OutputManager.add_error")
    mock_validate_properties_keys = mocker.patch(
        "RUFAS.input_validator.InputValidator._validate_metadata_properties_keys")
    info_map = {"class": "InputValidator", "function": "_metadata_array_validator"}

    if should_raise:
        with pytest.raises(ValueError):
            InputValidator._metadata_array_validator(key_path, value)
        assert mock_add_error.called
        assert mock_add_error.call_args[0] == (error_title, error_msg, info_map)
        mock_validate_properties_keys.assert_called_once()
    else:
        InputValidator._metadata_array_validator(key_path, value)
        mock_add_error.assert_not_called()
        mock_validate_properties_keys.assert_called_once()


def test_metadata_object_validator(
    mocker: MockerFixture,
) -> None:
    """Tests _metadata_object_validator() method in InputManager"""
    mock_validate_properties_keys = mocker.patch(
        "RUFAS.input_validator.InputValidator._validate_metadata_properties_keys")
    key_path = ["path", "cow"]
    value = {"type": "object", "description": "cow", "cow": {"data_about_cow": 17}}
    InputValidator._metadata_object_validator(key_path, value)
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
    mock_add_error = mocker.patch("RUFAS.output_manager.OutputManager.add_error")

    if should_raise:
        with pytest.raises(ValueError):
            InputValidator._validate_metadata_properties_keys(required_keys, valid_keys, properties, path)
        mock_add_error.assert_called_once_with(
            "Metadata Validation",
            expected_message,
            {
                "class": "InputValidator",
                "function": "_validate_metadata_properties_keys",
            },
        )
    else:
        InputValidator._validate_metadata_properties_keys(required_keys, valid_keys, properties, path)
        mock_add_error.assert_not_called()


def test_extract_input_data_by_key_list_no_error(mocker: MockerFixture) -> None:
    """Unit tests for making sure data were extracted when no error"""
    dummy_input_data: Dict[str, Any] = {"a": 1, "b": 2}
    dummy_var_path: list[str | int] = ["dummy_var_path"]
    dummy_var_properties: Dict[str, Any] = {"pattern": r"cow", "minimum_length": 1, "maximum_length": 5}
    dummy_value = 1
    patch_extract = mocker.patch.object(InputValidator, "extract_value_by_key_list", return_value=dummy_value)
    patch_log_missing_data = mocker.patch.object(InputValidator, "_log_missing_data")

    result = InputValidator._extract_input_data_by_key_list(
        input_data=dummy_input_data,
        variable_path=dummy_var_path,
        variable_properties=dummy_var_properties,
        called_during_initialization=True,
    )

    assert result == dummy_value
    patch_log_missing_data.assert_not_called()

    result = InputValidator._extract_input_data_by_key_list(
        input_data=dummy_input_data,
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
    var_path: List[str | int],
    var_name: str,
    called_during_initialization: bool,
    mocker: MockerFixture
) -> None:
    """Unit tests for making sure data were extracted when error occurs"""
    dummy_input_data: Dict[str, Any] = {"a": 1, "b": 2}
    dummy_var_properties: Dict[str, Any] = {"pattern": r"cow", "minimum_length": 1, "maximum_length": 5}
    patch_extract = mocker.patch.object(InputValidator, "extract_value_by_key_list", side_effect=KeyError)
    patch_log_missing_data = mocker.patch.object(InputValidator, "_log_missing_data")

    result = InputValidator._extract_input_data_by_key_list(
        input_data=dummy_input_data,
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

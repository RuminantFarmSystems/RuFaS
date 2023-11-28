from __future__ import annotations

from dataclasses import dataclass

import pytest
from pytest_mock import MockFixture

from RUFAS.routines.manure.IO_helpers.manure_module_output_manager_helper import ManureModuleOutputManagerHelper


@dataclass
class MockDataclass:
    """
    Mock data class for testing ManureModuleOutputManagerHelper.

    Attributes
    ----------
    field1 : int
        An integer field used for testing.
    field2 : str
        A string field used for testing.

    """

    field1: int
    field2: str


@pytest.mark.parametrize(
    "mock_data, exclude_fields, expected_calls",
    [
        ((10, "value"), None, [("field1", 10), ("field2", "value")]),
        ((10, "value"), ["field2"], [("field1", 10)]),
        ((5, "other_value"), None, [("field1", 5), ("field2", "other_value")]),
        ((5, "other_value"), ["field2"], [("field1", 5)])
    ]
)
def test_add_dataclass_object(mocker: MockFixture,
                              mock_data: tuple[int, str],
                              exclude_fields: list[str] | None,
                              expected_calls: list[tuple[str, int | str]]) -> None:
    """
    Unit test for add_dataclass_object() method in ManureModuleOutputManagerHelper.

    This test verifies that the method correctly adds the fields of a dataclass object to the output manager.
    It checks for the correct handling of the `exclude_fields` parameter.

    """

    # Arrange
    mock_add_variable = mocker.patch('RUFAS.output_manager.OutputManager.add_variable')

    obj = MockDataclass(field1=mock_data[0], field2=mock_data[1])
    info_maps = {'info_map1': 'value1', 'info_map2': 'value2', 'info_map3': 'value3'}

    # Act
    ManureModuleOutputManagerHelper.add_dataclass_object(obj, info_maps, exclude_fields)

    # Assert
    for field_name, value in expected_calls:
        mock_add_variable.assert_any_call(field_name, value, info_maps)

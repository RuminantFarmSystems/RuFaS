from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import pytest
from pytest_mock import MockFixture

from RUFAS.routines.manure.IO_helpers.manure_module_output_manager_helper import (
    ManureModuleOutputManagerHelper,
)
from RUFAS.units import MeasurementUnits


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

    field1_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS
    field2_unit: MeasurementUnits = MeasurementUnits.UNITLESS

    @property
    def units_dict(self) -> Dict[str, MeasurementUnits]:
        return {"field1_unit": MeasurementUnits.KILOGRAMS, "field2_unit": MeasurementUnits.UNITLESS}


@pytest.mark.parametrize(
    "mock_data, exclude_fields, expected_calls",
    [
        (
            (10, "value"),
            None,
            [
                ("field1", 10, {"info_map1": "value1", "units": MeasurementUnits.KILOGRAMS}),
                ("field2", "value", {"info_map1": "value1", "units": MeasurementUnits.UNITLESS}),
            ],
        ),
        ((10, "value"), ["field2"], [("field1", 10, {"info_map1": "value1", "units": MeasurementUnits.KILOGRAMS})]),
        (
            (5, "other_value"),
            None,
            [
                ("field1", 5, {"info_map1": "value1", "units": MeasurementUnits.KILOGRAMS}),
                ("field2", "other_value", {"info_map1": "value1", "units": MeasurementUnits.UNITLESS}),
            ],
        ),
        ((5, "other_value"), ["field2"], [("field1", 5, {"info_map1": "value1", "units": MeasurementUnits.KILOGRAMS})]),
    ],
)
def test_add_dataclass_object(
    mocker: MockFixture,
    mock_data: tuple[int, str],
    exclude_fields: list[str] | None,
    expected_calls: list[tuple[str, int | str, Dict[str, str]]],
) -> None:
    """
    Unit test for add_dataclass_object() method in ManureModuleOutputManagerHelper.

    This test verifies that the method correctly adds the fields of a dataclass object to the output manager.
    It checks for the correct handling of the `exclude_fields` parameter.

    """

    # Arrange
    mock_add_variable = mocker.patch("RUFAS.output_manager.OutputManager.add_variable")

    obj = MockDataclass(field1=mock_data[0], field2=mock_data[1])
    info_maps = {"info_map1": "value1"}

    # Act
    ManureModuleOutputManagerHelper.add_dataclass_object(obj, info_maps, exclude_fields)

    # Assert
    for field_name, value, info_map in expected_calls:
        mock_add_variable.assert_any_call(field_name, value, info_map)

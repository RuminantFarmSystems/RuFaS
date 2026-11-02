import logging
from typing import Any

import pytest
from pytest_mock import MockerFixture

from RUFAS.post_processing.unit_handler import UnitHandler


@pytest.fixture
def unit_handler() -> UnitHandler:
    return UnitHandler("test_prefix")


def test_unit_handler_init() -> None:
    """Unit test for the __init__ method of UnitHandler."""
    unit_handler = UnitHandler("test_prefix")

    assert unit_handler.metadata_prefix == "test_prefix"
    assert unit_handler._logger.name == "RUFAS.UnitHandler"


def test_unit_handler_init_default_metadata_prefix() -> None:
    """Unit test for the default metadata prefix of UnitHandler."""
    unit_handler = UnitHandler()

    assert unit_handler.metadata_prefix == ""


@pytest.mark.parametrize("level", [logging.INFO, logging.WARNING, logging.ERROR])
def test_log(level: int, unit_handler: UnitHandler, mocker: MockerFixture) -> None:
    """Unit test for the _log method of UnitHandler."""
    mock_logger_log = mocker.patch.object(unit_handler._logger, "log")

    unit_handler._log(level, "log_name", "log message", "function_name")

    mock_logger_log.assert_called_once_with(
        level,
        "log message",
        extra={
            "rufas_name": "log_name",
            "rufas_info_map": {
                "class": "UnitHandler",
                "function": "function_name",
                "metadata_prefix": "test_prefix",
            },
        },
    )


@pytest.mark.parametrize(
    "report_data, expected",
    [
        # Units given as a string
        (
            {"temperature": {"info_maps": [{"units": "Celsius"}], "values": [23, 24, 25]}},
            {"temperature (Celsius)": {"info_maps": [{"units": "Celsius"}], "values": [23, 24, 25]}},
        ),
        # Units given as a dictionary containing the variable name
        (
            {"pressure": {"info_maps": [{"units": {"pressure": "Pascal"}}], "values": [101325, 101300]}},
            {"pressure (Pascal)": {"info_maps": [{"units": {"pressure": "Pascal"}}], "values": [101325, 101300]}},
        ),
        # Units given as a dictionary that does not contain the variable name
        (
            {"pressure": {"info_maps": [{"units": {"other": "Pascal"}}], "values": [101325]}},
            {"pressure (not available)": {"info_maps": [{"units": {"other": "Pascal"}}], "values": [101325]}},
        ),
        # Only the units in the first info map are used
        (
            {"mass": {"info_maps": [{"units": "kg"}, {"units": "g"}], "values": [1, 2]}},
            {"mass (kg)": {"info_maps": [{"units": "kg"}, {"units": "g"}], "values": [1, 2]}},
        ),
        # Multiple variables
        (
            {
                "milk": {"info_maps": [{"units": "kg"}], "values": [30]},
                "cows": {"info_maps": [{"units": "animal"}], "values": [100]},
            },
            {
                "milk (kg)": {"info_maps": [{"units": "kg"}], "values": [30]},
                "cows (animal)": {"info_maps": [{"units": "animal"}], "values": [100]},
            },
        ),
        # No info maps in any variable
        ({"humidity": {"values": [80, 75, 70]}}, {"humidity": {"values": [80, 75, 70]}}),
        # No variables
        ({}, {}),
    ],
)
def test_add_var_units(
    report_data: dict[str, dict[str, list[Any]]],
    expected: dict[str, dict[str, list[Any]]],
    unit_handler: UnitHandler,
) -> None:
    """Unit test for the add_var_units method of UnitHandler."""
    assert unit_handler.add_var_units(report_data) == expected


def test_add_var_units_missing_info_maps(unit_handler: UnitHandler) -> None:
    """Unit test for the add_var_units method of UnitHandler when only some variables have info maps."""
    report_data: dict[str, dict[str, list[Any]]] = {
        "milk": {"info_maps": [{"units": "kg"}], "values": [30]},
        "cows": {"values": [100]},
    }

    with pytest.raises(KeyError):
        unit_handler.add_var_units(report_data)


@pytest.mark.parametrize(
    "constants_config, expected, expected_warnings",
    [
        # Constants matching GeneralConstants
        (
            {"LEAP_YEAR_LENGTH": 366, "FRACTION_TO_PERCENTAGE": 100.0},
            {"LEAP_YEAR_LENGTH_(day/leap year)": 366, "FRACTION_TO_PERCENTAGE_(unitless)": 100.0},
            [],
        ),
        # Constant names are normalized before they are matched to GeneralConstants
        (
            {"leap year length": 366, "KG to grams": 1000},
            {"leap year length_(day/leap year)": 366, "KG to grams_(g/kg)": 1000},
            [],
        ),
        # Constants not matching any GeneralConstants
        (
            {"SomeConstant": 10, "AnotherConstant": 5.5},
            {"SomeConstant_(unit_not_found)": 10, "AnotherConstant_(unit_not_found)": 5.5},
            ["SomeConstant", "AnotherConstant"],
        ),
        # Matching and non-matching constants
        (
            {"UnknownConstant": 100, "YEAR_LENGTH": 365},
            {"UnknownConstant_(unit_not_found)": 100, "YEAR_LENGTH_(day/year)": 365},
            ["UnknownConstant"],
        ),
        # Constant matching an attribute of GeneralConstants that has no units
        ({"CONSTANTS_TO_UNITS": 1}, {"CONSTANTS_TO_UNITS_(unit_not_found)": 1}, []),
        # No constants
        ({}, {}, []),
    ],
)
def test_add_units_to_constants(
    constants_config: dict[str, int | float],
    expected: dict[str, int | float],
    expected_warnings: list[str],
    unit_handler: UnitHandler,
    mocker: MockerFixture,
) -> None:
    """Unit test for the add_units_to_constants method of UnitHandler."""
    mock_log = mocker.patch.object(unit_handler, "_log")

    result = unit_handler.add_units_to_constants(constants_config)

    assert result == expected
    assert mock_log.call_args_list == [
        mocker.call(
            logging.WARNING,
            "report_generation_warning",
            f"No matching GeneralConstant found for filter constant {name}.",
            "add_units_to_constants",
        )
        for name in expected_warnings
    ]


@pytest.mark.parametrize(
    "input_name, expected_output",
    [
        ("CONSTANT_NAME", "constantname"),
        ("  constant   name ", "constantname"),
        ("ConstantName", "constantname"),
        ("constant_name", "constantname"),
        ("CONSTANT__NAME", "constantname"),
        ("constant name", "constantname"),
        ("CONSTANT NAME", "constantname"),
        (" constant _ Name ", "constantname"),
        ("", ""),
    ],
)
def test_normalize_constant_name(input_name: str, expected_output: str, unit_handler: UnitHandler) -> None:
    """Unit test for the _normalize_constant_name method of UnitHandler."""
    assert unit_handler._normalize_constant_name(input_name) == expected_output


@pytest.mark.parametrize(
    "report_data, operation, simplify_units, expected",
    [
        # A single column keeps its units
        ({"temperature (Celsius)": [23.0, 24.0, 25.0]}, "sum", False, "Celsius"),
        ({"wind_speed (m/s)": [10.0, 12.0, 15.0]}, "average", True, "m/s"),
        ({"temperature": [23.0, 24.0, 25.0]}, "sum", True, ""),
        # More than two columns keep the units of the first column
        ({"a (kg)": [1.0], "b (L)": [2.0], "c (m)": [3.0]}, "product", True, "kg"),
        ({"a": [1.0], "b (L)": [2.0], "c (m)": [3.0]}, "sum", True, ""),
        # Units of two columns are combined
        ({"a (kg)": [1.0], "b (m)": [2.0]}, "product", True, "kg*m"),
        ({"a (m^2)": [1.0], "b (m)": [2.0]}, "product", True, "m^3"),
        ({"a (kg/day)": [1.0], "b (day)": [2.0]}, "product", True, "kg"),
        ({"a (kg/day)": [1.0], "b (day)": [2.0]}, "product", False, "kg*day/day"),
        ({"milk (kg)": [1.0], "cows (animal)": [2.0]}, "division", True, "kg/animal"),
        ({"a (kg*day/animal)": [1.0], "b (day)": [2.0]}, "division", True, "kg/animal"),
        ({"a (kg)": [1.0], "b (kg)": [2.0]}, "division", True, "unitless"),
        ({"a (kg)": [1.0], "b (kg)": [2.0]}, "division", False, "kg/kg"),
        ({"a (kg)": [1.0], "b (kg)": [2.0]}, "sum", True, "kg"),
        ({"a (kg)": [1.0], "b (L)": [2.0]}, "subtraction", True, "kg"),
        ({"a": [1.0], "b": [2.0]}, "average", True, "unitless"),
        ({"a (kg)": [1.0], "b (kg)": [2.0]}, None, True, "kg"),
    ],
)
def test_aggregate_units(
    report_data: dict[str, list[Any]],
    operation: str | None,
    simplify_units: bool,
    expected: str,
    unit_handler: UnitHandler,
    mocker: MockerFixture,
) -> None:
    """Unit test for the aggregate_units method of UnitHandler."""
    mocker.patch.object(unit_handler, "_log")

    assert unit_handler.aggregate_units(report_data, operation, simplify_units) == expected


def test_aggregate_units_combines_units_of_two_columns(unit_handler: UnitHandler, mocker: MockerFixture) -> None:
    """Unit test for the aggregate_units method of UnitHandler when there are two columns to aggregate."""
    mock_combine_units = mocker.patch.object(unit_handler, "combine_units", return_value=({"kg": 1}, {"animal": 1}))

    result = unit_handler.aggregate_units({"milk (kg/day)": [1.0], "cows (animal)": [2.0]}, "division", False)

    assert result == "kg/animal"
    mock_combine_units.assert_called_once_with({"kg": 1}, {"day": 1}, {"animal": 1}, {}, "division", False)


def test_aggregate_units_no_report_data(unit_handler: UnitHandler) -> None:
    """Unit test for the aggregate_units method of UnitHandler when there is no report data."""
    with pytest.raises(ValueError, match="No report data available to aggregate units from."):
        unit_handler.aggregate_units({}, "sum", True)


@pytest.mark.parametrize(
    "numerator1, denominator1, numerator2, denominator2, operation, simplify_units, expected, expect_warning",
    [
        # Product
        ({"kg": 1}, {"day": 1}, {"day": 1}, {}, "product", True, ({"kg": 1}, {}), False),
        ({"kg": 1}, {"day": 1}, {"day": 1}, {}, "product", False, ({"kg": 1, "day": 1}, {"day": 1}), False),
        ({"m": 1}, {"s": 1}, {"m": 1}, {"s": 1}, "product", True, ({"m": 2}, {"s": 2}), False),
        # Division
        ({"kg": 1}, {}, {"animal": 1}, {"day": 1}, "division", True, ({"kg": 1, "day": 1}, {"animal": 1}), False),
        ({"kg": 1}, {}, {"kg": 1}, {}, "division", True, ({}, {}), False),
        ({"kg": 1}, {}, {"kg": 1}, {}, "division", False, ({"kg": 1}, {"kg": 1}), False),
        # Operations that keep the units, with matching units
        ({"kg": 1}, {"day": 1}, {"kg": 1}, {"day": 1}, "sum", True, ({"kg": 1}, {"day": 1}), False),
        ({"kg": 1}, {"day": 1}, {"kg": 1}, {"day": 1}, "average", False, ({"kg": 1}, {"day": 1}), False),
        # Operations that keep the units, with different units
        ({"kg": 1}, {"day": 1}, {"g": 1}, {"day": 1}, "subtraction", True, ({"kg": 1}, {"day": 1}), True),
        ({"kg": 1}, {"day": 1}, {"kg": 1}, {"year": 1}, "SD", True, ({"kg": 1}, {"day": 1}), True),
        # Operations that are not supported aggregation functions
        ({"kg": 1}, {}, {"kg": 1}, {}, "bad_aggregator_function", True, ({"kg": 1}, {}), False),
        ({"kg": 1}, {}, {"L": 1}, {}, None, True, ({"kg": 1}, {}), True),
    ],
)
def test_combine_units(
    numerator1: dict[str, int],
    denominator1: dict[str, int],
    numerator2: dict[str, int],
    denominator2: dict[str, int],
    operation: str | None,
    simplify_units: bool,
    expected: tuple[dict[str, int], dict[str, int]],
    expect_warning: bool,
    unit_handler: UnitHandler,
    mocker: MockerFixture,
) -> None:
    """Unit test for the combine_units method of UnitHandler."""
    mock_log = mocker.patch.object(unit_handler, "_log")

    result = unit_handler.combine_units(numerator1, denominator1, numerator2, denominator2, operation, simplify_units)

    assert result == expected
    if expect_warning:
        mock_log.assert_called_once_with(
            logging.WARNING,
            "Report Generator Units Warning",
            f"Report units do not match for operation {operation}.",
            "combine_units",
        )
    else:
        mock_log.assert_not_called()


def test_combine_units_does_not_change_units(unit_handler: UnitHandler) -> None:
    """Unit test for the combine_units method of UnitHandler to check the units passed to it are left unchanged."""
    numerator1, denominator1 = {"kg": 1}, {"day": 1}
    numerator2, denominator2 = {"kg": 1}, {"day": 1}

    combined_numerator, combined_denominator = unit_handler.combine_units(
        numerator1, denominator1, numerator2, denominator2, "sum", True
    )
    combined_numerator["kg"] = 2
    combined_denominator["day"] = 2

    assert numerator1 == {"kg": 1}
    assert denominator1 == {"day": 1}

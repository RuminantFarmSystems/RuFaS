from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Type
from unittest.mock import patch

import numpy as np
import pytest
from pytest_mock import MockerFixture

from RUFAS.graph_generator import GraphGenerator
from RUFAS.report_generator import AGGREGATION_FUNCTIONS, ReportGenerator


class MockUtility:
    @staticmethod
    def convert_list_of_dicts_to_dict_of_lists(data: List[Dict[str, Any]]) -> Dict[str, List[Any]]:
        return {k: [dic[k] for dic in data] for k in data[0]}


Utility = MockUtility


@pytest.fixture
def report_generator() -> ReportGenerator:
    return ReportGenerator()


@pytest.fixture
def sample_filtered_pool() -> Dict[str, Dict[str, List[Dict[str, int]]]]:
    return {
        "data1": {"values": [{"a": 1, "b": 2, "c": 10}, {"a": 3, "b": 4, "c": 10}]},
        "data2": {"values": [{"a": 5, "b": 6, "c": 10}, {"a": 7, "b": 8, "c": 10}]},
    }


@pytest.mark.parametrize(
    "report_data, aggregator_key, expected",
    [
        # Tests with sum aggregator
        (
            {"a": [1, 2], "b": [3, 4]},
            "sum",
            ({"a": [3], "b": [7]}, [{"mock_log": "mock_log_msg"}, {"mock_log": "mock_log_msg"}]),
        ),
        (
            {"a": [1, 2, 3], "b": [4, 5, 6]},
            "sum",
            ({"a": [6], "b": [15]}, [{"mock_log": "mock_log_msg"}, {"mock_log": "mock_log_msg"}]),
        ),
        # Tests with product aggregator
        (
            {"a": [1, 2], "b": [3, 4]},
            "product",
            ({"a": [2], "b": [12]}, [{"mock_log": "mock_log_msg"}, {"mock_log": "mock_log_msg"}]),
        ),
        (
            {"a": [1, 2, 3], "b": [4, 5, 6]},
            "product",
            ({"a": [6], "b": [120]}, [{"mock_log": "mock_log_msg"}, {"mock_log": "mock_log_msg"}]),
        ),
        # Tests with average aggregator
        (
            {"a": [1, 2, 3], "b": [4, 5, 6]},
            "average",
            ({"a": [2.0], "b": [5.0]}, [{"mock_log": "mock_log_msg"}, {"mock_log": "mock_log_msg"}]),
        ),
        (
            {"a": [1, 2, 3, 4], "b": [5, 6, 7, 8]},
            "average",
            ({"a": [2.5], "b": [6.5]}, [{"mock_log": "mock_log_msg"}, {"mock_log": "mock_log_msg"}]),
        ),
        # Tests with division aggregator
        (
            {"a": [8, 4], "b": [2, 1]},
            "division",
            ({"a": [2.0], "b": [2.0]}, [{"mock_log": "mock_log_msg"}, {"mock_log": "mock_log_msg"}]),
        ),
        (
            {"a": [8, 4, 2], "b": [2, 1, 1]},
            "division",
            ({"a": [1.0], "b": [2.0]}, [{"mock_log": "mock_log_msg"}, {"mock_log": "mock_log_msg"}]),
        ),
        # Tests with standard deviation aggregator
        (
            {"a": [10, 12, 23, 23], "b": [17, 15, 22, 20]},
            "SD",
            (
                {"a": [6.041522986797286], "b": [2.692582403567252]},
                [{"mock_log": "mock_log_msg"}, {"mock_log": "mock_log_msg"}],
            ),
        ),
        (
            {"a": [10, 12, 23, 23, 23], "b": [17, 15, 22, 20, 20]},
            "SD",
            (
                {"a": [5.912698199637793], "b": [2.481934729198171]},
                [{"mock_log": "mock_log_msg"}, {"mock_log": "mock_log_msg"}],
            ),
        ),
        # Test with None values in data
        (
            {"a": [1, None], "b": [None, 4]},
            "sum",
            ({"a": [1], "b": [4]}, [{"mock_log": "mock_log_msg"}, {"mock_log": "mock_log_msg"}]),
        ),
    ],
)
def test_apply_vertical_aggregation(
    report_data: dict[str, dict[str, list[float | None]]] | dict[str, list[float | None]],
    aggregator_key: str,
    expected: tuple[dict[str, list[float]], list[dict[str, str]]],
    mocker: MockerFixture,
) -> None:
    """
    Unit test for _apply_vertical_aggregation() method in report_generator.py file.
    """

    # Arrange
    aggregator = AGGREGATION_FUNCTIONS[aggregator_key]
    mock_time = mocker.MagicMock()
    report_generator = ReportGenerator(time=mock_time)

    mocker.patch.object(
        report_generator,
        "_handle_aggregation",
        side_effect=[
            (expected[0]["a"][0], {"mock_log": "mock_log_msg"}),
            (expected[0]["b"][0], {"mock_log": "mock_log_msg"}),
        ],
    )

    # Act
    result = report_generator._apply_vertical_aggregation(report_data, aggregator)

    # Assert
    assert result == expected


@pytest.mark.parametrize(
    "report_data, loop_list, aggregator_key, expected, expected_exception",
    [
        # Tests with sum aggregation
        ({"a": [1, 2], "b": [3, 4]}, ["a", "b"], "sum", ([4, 6], "unitless", []), None),
        ({"a": [1, 2, 3], "b": [4, 5, 6]}, ["a", "b"], "sum", ([5, 7, 9], "unitless", []), None),
        # Tests with subtraction aggregation
        ({"a": [1, 2], "b": [3, 4]}, ["a", "b"], "subtraction", ([-2, -2], "unitless", []), None),
        (
            {"a": [1, 2, 3], "b": [4, 5, 6]},
            ["a", "b"],
            "subtraction",
            ([-3, -3, -3], "unitless", []),
            None,
        ),
        # Tests with product aggregation
        ({"a": [1, 2], "b": [3, 4]}, ["a", "b"], "product", ([3, 8], "unitless", []), None),
        ({"a": [1, 2, 3], "b": [4, 5, 6]}, ["a", "b"], "product", ([4, 10, 18], "unitless", []), None),
        # Tests with division aggregation
        (
            {"a": [1, 2], "b": [3, 4]},
            ["a", "b"],
            "division",
            ([0.3333333333333333, 0.5], "unitless", []),
            None,
        ),
        (
            {"a": [1, 2, 3], "b": [4, 5, 6]},
            ["a", "b"],
            "division",
            ([0.25, 0.4, 0.5], "unitless", []),
            None,
        ),
        # Tests with average aggregation
        ({"a": [1, 3], "b": [2, 4]}, ["a", "b"], "average", ([1.5, 3.5], "unitless", []), None),
        (
            {"a": [1, 2, 3], "b": [4, 5, 6]},
            ["a", "b"],
            "average",
            ([2.5, 3.5, 4.5], "unitless", []),
            None,
        ),
        # Tests with standard deviation aggregation
        ({"a": [10, 10], "b": [20, 20]}, ["a", "b"], "SD", ([5.0, 5.0], "unitless", []), None),
        (
            {"a": [10, 12, 23, 23], "b": [17, 15, 22, 20]},
            ["a", "b"],
            "SD",
            ([3.5, 1.5, 0.5, 1.5], "unitless", []),
            None,
        ),
        # Tests with inconsistent lengths
        ({"a": [1, 2, 3], "b": [3, 4]}, ["a", "b"], "sum", None, ValueError),
    ],
)
def test_apply_horizontal_aggregation(
    report_data: Dict[str, List[float]],
    loop_list: List[str],
    aggregator_key: str,
    expected: tuple[list[float], str, list[dict[str, str | dict[str, str]]]],
    expected_exception: Type[Exception] | None,
    mocker: MockerFixture,
) -> None:
    """
    Unit test for _apply_horizontal_aggregation() static method in report_generator.py file.
    """

    # Arrange
    aggregator = AGGREGATION_FUNCTIONS[aggregator_key]
    mock_time = mocker.MagicMock()
    report_generator = ReportGenerator(time=mock_time)
    simplify_units = True

    # Act and assert
    if expected_exception:
        with pytest.raises(expected_exception):
            report_generator._apply_horizontal_aggregation(report_data, loop_list, aggregator, simplify_units)
    else:
        result = report_generator._apply_horizontal_aggregation(report_data, loop_list, aggregator, simplify_units)
        assert result == expected


@pytest.mark.parametrize(
    "report_data, filter_content, expected_report_data, expected_exception",
    [
        # Valid case with a valid constant
        (
            {"existing_data": [1, 2, 3]},
            {"constants": {"Constant1": 10}},
            {
                "existing_data": [1, 2, 3],
                "Constant1": [10, 10, 10],
            },
            None,
        ),
        # Valid case with a valid constant and display_units as True
        (
            {"existing_data": [1, 2, 3]},
            {"constants": {"Constant1": 10}, "display_units": True},
            {
                "existing_data": [1, 1, 1],
                "Constant1": [10, 10, 10],
            },
            None,
        ),
        # Valid case with existing data of different lengths
        (
            {"col1": [1, 2, 3], "col2": [4, 5, 6, 7]},
            {"constants": {"Constant1": 10}},
            {"col1": [1, 2, 3], "col2": [4, 5, 6, 7], "Constant1": [10, 10, 10, 10]},
            None,
        ),
        # Valid case with no constants
        ({"existing_data": [1, 2, 3]}, {}, {"existing_data": [1, 2, 3]}, None),
        # Error case with a constant name that already exists in report_data
        ({"Constant1": [5, 5, 5]}, {"constants": {"Constant1": 10}}, None, ValueError),
    ],
)
def test_add_constants_to_report_data(
    report_data: Dict[str, List[Any]],
    filter_content: Dict[str, Any],
    expected_report_data: Dict[str, List[Any]],
    expected_exception: Type[Exception] | None,
    mocker: MockerFixture,
) -> None:
    """
    Unit test for the _add_constants_to_report_data static method in report_generator.py file.
    """

    # Arrange
    mock_time = mocker.MagicMock()
    report_generator = ReportGenerator(time=mock_time)
    display_units = filter_content.get("display_units", False)
    mock_rg_add_units_to_constants = mocker.patch.object(
        report_generator, "_add_units_to_constants", return_value=[{"existing_data": 1, "Constant1": 10}, []]
    )

    # Act and assert
    if expected_exception:
        with pytest.raises(expected_exception):
            report_generator._add_constants_to_report_data(report_data, filter_content)
    else:
        report_generator._add_constants_to_report_data(report_data, filter_content)
        assert report_data == expected_report_data

    if display_units:
        mock_rg_add_units_to_constants.assert_called_once()
    else:
        mock_rg_add_units_to_constants.assert_not_called()


@pytest.mark.parametrize(
    "report_data, constant_config, expected_exception",
    [
        # Valid case with valid constants
        ({}, {"Constant1": 10, "Constant2": 20.5}, None),
        # Error case with repeated constant name
        ({"Constant1": [5, 5, 5]}, {"Constant1": 10}, ValueError),
        # Error case with constant name None
        ({}, {None: 10}, ValueError),
        # Error case with constant value None
        ({}, {"Constant1": None}, ValueError),
        # Error case with constant name not a string
        ({}, {123: 10}, ValueError),
        # Error case with constant value not a number
        ({}, {"Constant1": "not_a_number"}, ValueError),
        # Error case with an empty constant name
        ({}, {"": 10}, ValueError),
    ],
)
def test_validate_constants(
    report_data: Dict[str, List[Any]],
    constant_config: Dict[str, Any],
    expected_exception: Type[Exception] | None,
    mocker: MockerFixture,
) -> None:
    """
    Unit test for the _validate_constants static method in report_generator.py file.
    """

    # Arrange
    mock_time = mocker.MagicMock()
    report_generator = ReportGenerator(time=mock_time)

    # Act and assert
    if expected_exception:
        with pytest.raises(expected_exception):
            report_generator._validate_constants(report_data, constant_config)
    else:
        report_generator._validate_constants(report_data, constant_config)


@pytest.mark.parametrize(
    "constants_config, expected_result",
    [
        (
            {"SomeConstant": 10, "AnotherConstant": 5.5},
            (
                {"SomeConstant_(unit_not_found)": 10, "AnotherConstant_(unit_not_found)": 5.5},
                [
                    {
                        "warning": "report_generation_warning",
                        "message": "No matching GeneralConstant found for filter constant SomeConstant.",
                        "info_map": {"class": "ReportGenerator", "function": "_add_units_to_constants"},
                    },
                    {
                        "warning": "report_generation_warning",
                        "message": "No matching GeneralConstant found for filter constant AnotherConstant.",
                        "info_map": {"class": "ReportGenerator", "function": "_add_units_to_constants"},
                    },
                ],
            ),
        ),
        (
            {"LEAP_YEAR_LENGTH": 366, "FRACTION_TO_PERCENTAGE": 100.0},
            ({"LEAP_YEAR_LENGTH_(day/leap year)": 366, "FRACTION_TO_PERCENTAGE_(unitless)": 100.0}, []),
        ),
        (
            {"UnknownConstant": 100},
            (
                {"UnknownConstant_(unit_not_found)": 100},
                [
                    {
                        "info_map": {"class": "ReportGenerator", "function": "_add_units_to_constants"},
                        "message": "No matching GeneralConstant found for filter constant " "UnknownConstant.",
                        "warning": "report_generation_warning",
                    }
                ],
            ),
        ),
        (
            {},
            ({}, []),
        ),
    ],
)
def test_add_units_to_constants(
    constants_config: dict[str, int | float],
    expected_result: tuple[dict[str, int | float], list[dict[str, str | dict[str, str]]]],
) -> None:
    """
    Test the _add_units_to_constants method to ensure that units are correctly appended to constants.
    """
    report_generator = ReportGenerator()
    result = report_generator._add_units_to_constants(constants_config)
    assert result == expected_result


@pytest.mark.parametrize(
    "filtered_pool, filter_content, mock_agg_keys, mock_aggregator_return_value, expected_output",
    [
        (
            # Test case 1: No aggregation specified
            {"col1": {"values": [1, 2, 3]}, "col2": {"values": [4, 5, 6]}},
            {"display_units": False, "filters": [], "name": "test1"},
            (None, None),
            None,
            ({"col1": [1, 2, 3], "col2": [4, 5, 6]}, [], False),
        ),
        (
            # Test case 2: Horizontal aggregation only
            {"col1": {"values": [1, 2, 3]}, "col2": {"values": [4, 5, 6]}},
            {"display_units": False, "horizontal_agg": "sum", "filters": [], "name": "test2"},
            ("sum", None),
            ({"hor_agg": [6, 15]}, []),
            ({"hor_agg": [6, 15]}, [], True),
        ),
        (
            # Test case 3: Vertical aggregation only
            {"col1": {"values": [1, 2, 3]}, "col2": {"values": [4, 5, 6]}},
            {"display_units": False, "vertical_agg": "sum", "filters": [], "name": "test3"},
            (None, "sum"),
            ({"ver_agg": [5, 7, 9]}, []),
            ({"ver_agg": [5, 7, 9]}, [], True),
        ),
        (
            # Test case 4: Both horizontal and vertical aggregations, horizontal first
            {"col1": {"values": [1, 2, 3]}, "col2": {"values": [4, 5, 6]}},
            {
                "display_units": False,
                "horizontal_agg": "sum",
                "vertical_agg": "sum",
                "horizontal_first": True,
                "filters": [],
                "name": "test4",
            },
            ("sum", "sum"),
            ({"hor_ver_agg": [21]}, []),
            ({"hor_ver_agg": [21]}, [], True),
        ),
        (
            # Test case 5: Both horizontal and vertical aggregations, vertical first
            {"col1": {"values": [1, 2, 3]}, "col2": {"values": [4, 5, 6]}},
            {
                "display_units": False,
                "horizontal_agg": "sum",
                "vertical_agg": "sum",
                "horizontal_first": False,
                "filters": [],
                "name": "test5",
            },
            ("sum", "sum"),
            ({"ver_hor_agg": [21]}, []),
            ({"ver_hor_agg": [21]}, [], True),
        ),
        (
            # Test case 6: No aggregation specified
            {
                "col1": {"values": [1, 2, 3], "info_maps": [{"units": "dummy_units"}]},
                "col2": {"values": [4, 5, 6], "info_maps": [{"units": "dummy_units2"}]},
            },
            {"display_units": True, "filters": [], "name": "test1"},
            (None, None),
            None,
            ({"col1 (dummy_units)": [1, 2, 3], "col2 (dummy_units2)": [4, 5, 6]}, [], False),
        ),
    ],
)
def test_perform_aggregations(
    filtered_pool: dict[str, dict[str, list[Any]]],
    filter_content: dict[str, Any],
    mock_agg_keys: tuple[str | None, str | None],
    mock_aggregator_return_value: dict[str, list[Any]],
    expected_output: tuple[dict[str, list[Any]], list[dict[str, str | dict[str, str]]]],
    mocker: MockerFixture,
) -> None:
    report_generator = ReportGenerator()

    mocker.patch.object(report_generator, "_extract_aggregation_keys", return_value=mock_agg_keys)

    if mock_agg_keys[0] is not None or mock_agg_keys[1] is not None:
        mocker.patch.object(report_generator, "_route_aggregator_functions", return_value=mock_aggregator_return_value)
        result = report_generator._perform_aggregations(filtered_pool, filter_content)
    else:
        result = report_generator._perform_aggregations(filtered_pool, filter_content)

    assert result == expected_output


@pytest.mark.parametrize(
    "report_data, filter_content, horizontal_agg_key, vertical_agg_key, expected_report, expected_logs",
    [
        (
            {"data": [1, 2, 3]},
            {"display_units": False},
            "sum",
            "sum",
            {"ver_hor_agg": [6]},
            [
                {
                    "log": "Report 'Unnamed Report' aggregation variables.",
                    "message": "Variables/constants aggregated: ['data'].",
                    "info_map": {"class": "ReportGenerator", "function": "_route_aggregator_functions"},
                }
            ],
        ),
        (
            {"data_(km)": [1, 2, 3]},
            {"display_units": True},
            "sum",
            None,
            {"hor_agg_(km)": [1, 2, 3]},
            [
                {
                    "log": "Report 'Unnamed Report' aggregation variables.",
                    "message": "Variables/constants aggregated: ['data_(km)'].",
                    "info_map": {"class": "ReportGenerator", "function": "_route_aggregator_functions"},
                }
            ],
        ),
        (
            {"data": [1, 2, 3]},
            {"display_units": False},
            "sum",
            None,
            {"hor_agg": [1, 2, 3]},
            [
                {
                    "log": "Report 'Unnamed Report' aggregation variables.",
                    "message": "Variables/constants aggregated: ['data'].",
                    "info_map": {"class": "ReportGenerator", "function": "_route_aggregator_functions"},
                }
            ],
        ),
        (
            {"data": [1, 2, 3]},
            {"display_units": True},
            None,
            None,
            {"data": [1, 2, 3]},
            [
                {
                    "log": "Report 'Unnamed Report' aggregation variables.",
                    "message": "Variables/constants aggregated: ['data'].",
                    "info_map": {"class": "ReportGenerator", "function": "_route_aggregator_functions"},
                }
            ],
        ),
        (
            {"data": [1, 2, 3]},
            {"display_units": True, "variables": "data"},
            None,
            "sum",
            {"ver_agg": [6]},
            [
                {
                    "log": "Report 'Unnamed Report' aggregation variables.",
                    "message": "Variables/constants aggregated: ['data'].",
                    "info_map": {"class": "ReportGenerator", "function": "_route_aggregator_functions"},
                }
            ],
        ),
        (
            {"data_(kg)": [1, 2, 3]},
            {"display_units": True},
            None,
            "sum",
            {"ver_agg_(kg)": [6]},
            [
                {
                    "log": "Report 'Unnamed Report' aggregation variables.",
                    "message": "Variables/constants aggregated: ['data_(kg)'].",
                    "info_map": {"class": "ReportGenerator", "function": "_route_aggregator_functions"},
                }
            ],
        ),
        (
            {"data": [1, 2, 3]},
            {"display_units": False, "variables": "data"},
            None,
            "sum",
            {"ver_agg": [6]},
            [
                {
                    "log": "Report 'Unnamed Report' aggregation variables.",
                    "message": "Variables/constants aggregated: ['data'].",
                    "info_map": {"class": "ReportGenerator", "function": "_route_aggregator_functions"},
                }
            ],
        ),
        (
            {"data": [1, 2, 3]},
            {"display_units": False},
            None,
            "sum",
            {"ver_agg": [6]},
            [
                {
                    "log": "Report 'Unnamed Report' aggregation variables.",
                    "message": "Variables/constants aggregated: ['data'].",
                    "info_map": {"class": "ReportGenerator", "function": "_route_aggregator_functions"},
                }
            ],
        ),
        (
            {"data": [1, 2, 3]},
            {"display_units": True},
            None,
            "sum",
            {"ver_agg": [6]},
            [
                {
                    "log": "Report 'Unnamed Report' aggregation variables.",
                    "message": "Variables/constants aggregated: ['data'].",
                    "info_map": {"class": "ReportGenerator", "function": "_route_aggregator_functions"},
                }
            ],
        ),
    ],
)
def test_route_aggregator_functions(
    report_data: dict[str, dict[str, list[Any]]],
    filter_content: dict[str, Any],
    horizontal_agg_key: str,
    vertical_agg_key: str,
    expected_report: dict[str, list[Any]],
    expected_logs: list[Any],
) -> None:
    generator = ReportGenerator()
    result_report, result_logs = generator._route_aggregator_functions(
        report_data, filter_content, horizontal_agg_key, vertical_agg_key
    )
    assert result_report == expected_report, f"Expected report {expected_report} but got {result_report}"
    assert result_logs == expected_logs, f"Expected logs {expected_logs} but got {result_logs}"


@pytest.mark.parametrize(
    "key, expected",
    [
        ("temperature (C)", "temperature_ver_agg_(C)"),
        ("pressure (Pa)", "pressure_ver_agg_(Pa)"),
        ("velocity (m/s)", "velocity_ver_agg_(m/s)"),
        ("volume (m^3)", "volume_ver_agg_(m^3)"),
        ("density (kg/m^3)", "density_ver_agg_(kg/m^3)"),
        ("energy", "energy_ver_agg"),
        ("power (W)", "power_ver_agg_(W)"),
        ("", "_ver_agg"),
    ],
)
def test_update_key(key: str, expected: str) -> None:
    generator = ReportGenerator()
    result = generator._update_key(key)
    assert result == expected, f"For key '{key}', expected '{expected}' but got '{result}'"


@pytest.mark.parametrize(
    "numerator1, denominator1, numerator2, denominator2, operation, expected_numerator, expected_denominator,"
    "expected_logs",
    [
        ({"m": 1}, {"s": -1}, {"m": 1}, {"s": -1}, "product", {"m": 2}, {"s": -2}, {}),
        ({"m": 1}, {"s": -1}, {"s": -1}, {"m": 1}, "division", {"m": 2}, {"s": -2}, {}),
        (
            {"m": 1},
            {"ks": -1},
            {"m": 1},
            {"s": -1},
            "sum",
            {"m": 1},
            {"ks": -1},
            {
                "warning": "Report Generator Units Warning",
                "message": "Report units do not match for operation sum.",
                "info_map": {"class": "type", "function": "_combine_units"},
            },
        ),
        ({"m": 1}, {"s": -1}, {"kg": 1}, {"m": 1}, "product", {"kg": 1}, {"s": -1}, {}),
        ({"m": 1}, {"s": -1}, {"kg": 1}, {"m": 1}, "division", {"m": 2}, {"s": -1, "kg": 1}, {}),
        (
            {"km": 1},
            {"s": -1},
            {"m": 1},
            {"s": -1},
            "subtraction",
            {"km": 1},
            {"s": -1},
            {
                "warning": "Report Generator Units Warning",
                "message": "Report units do not match for operation subtraction.",
                "info_map": {"class": "type", "function": "_combine_units"},
            },
        ),
        (
            {"km": 1},
            {"s": -1},
            {"m": 1},
            {"s": -1},
            "bad_aggregator_function",
            {"km": 1},
            {"s": -1},
            {
                "warning": "Report Generator Aggregator Operation Warning",
                "message": "Aggregator operation bad_aggregator_function does not match any current "
                "aggregator functions: ['average', 'division', 'product', 'SD', 'sum', 'subtraction'].",
                "info_map": {"class": "type", "function": "_combine_units"},
            },
        ),
    ],
)
def test_combine_units(
    numerator1: dict[str, int],
    denominator1: dict[str, int],
    numerator2: dict[str, int],
    denominator2: dict[str, int],
    operation: str,
    expected_numerator: dict[str, int],
    expected_denominator: dict[str, int],
    expected_logs: dict[str, str | dict[str, str]],
) -> None:
    generator = ReportGenerator()
    simplify_units = True
    result_numerator, result_denominator, result_logs = generator._combine_units(
        numerator1, denominator1, numerator2, denominator2, operation, simplify_units
    )
    assert result_numerator == expected_numerator, f"For operation '{operation}',"
    f" expected numerator {expected_numerator} but got {result_numerator}"
    assert result_denominator == expected_denominator, f"For operation '{operation}', "
    f"expected denominator {expected_denominator} but got {result_denominator}"


@pytest.mark.parametrize(
    "aggregate_report, horizontal_agg_key, vertical_agg_key, filter_content, mock_horizontal_agg,"
    "mock_vertical_agg, expected_output",
    [
        (
            # Test case 1: Horizontal first with sum aggregations
            {"col1": [1, 2, 3], "col2": [4, 5, 6]},
            "sum",
            "sum",
            {"horizontal_first": True, "display_units": False},
            ([10], "units", []),
            21,
            ({"hor_ver_agg": [21]}, [{"mock_log": "mock_log_msg"}]),
        ),
        (
            # Test case 2: Vertical first with sum aggregations
            {"col1": [1, 2, 3], "col2": [4, 5, 6]},
            "sum",
            "sum",
            {"horizontal_first": False, "display_units": False},
            None,
            ({"col1": [5], "col2": [7]}, []),
            (
                {
                    "ver_hor_agg": [
                        (
                            {"col1": [5], "col2": [7]},
                            [{"mock_log": "mock_log_msg"}, {"mock_units_log": "mock_units_msg"}],
                        )
                    ]
                },
                [{"mock_log": "mock_log_msg"}, {"mock_units_log": "mock_units_msg"}],
            ),
        ),
        (
            # Test case 3: horizontal first with sum aggregations, displays units
            {"col1_(dummy_units)": [1, 2, 3], "col2_(dummy_units)": [4, 5, 6]},
            "sum",
            "sum",
            {"horizontal_first": True, "display_units": True},
            None,
            {"col1_(kg)": [5], "col2_(Mj)": [7]},
            (
                {"hor_ver_agg_(dummy_units)": [{"col1_(kg)": [5], "col2_(Mj)": [7]}]},
                [
                    {"mock_log": "mock_log_msg"},
                    {"mock_log": "mock_log_msg"},
                    {"mock_log": "mock_log_msg"},
                    {"mock_units_log": "mock_units_msg"},
                    {"mock_log": "mock_log_msg"},
                ],
            ),
        ),
        (
            # Test case 2: Vertical first with sum aggregations
            {"col1_(dummy_units)": [1, 2, 3], "col2_(dummy_units)": [4, 5, 6]},
            "sum",
            "sum",
            {"horizontal_first": False, "display_units": True},
            None,
            ({"col1": [5], "col2": [7]}, []),
            (
                {
                    "ver_hor_agg_(dummy_units)": [
                        (
                            {"col1": [5], "col2": [7]},
                            [{"mock_log": "mock_log_msg"}, {"mock_units_log": "mock_units_msg"}],
                        )
                    ]
                },
                [{"mock_log": "mock_log_msg"}, {"mock_units_log": "mock_units_msg"}],
            ),
        ),
    ],
)
def test_handle_horizontal_and_vertical_aggregations(
    aggregate_report: dict[str, list[Any]],
    horizontal_agg_key: str,
    vertical_agg_key: str,
    filter_content: dict[str, Any],
    mock_horizontal_agg: Any,
    mock_vertical_agg: Any,
    expected_output: tuple[dict[str, list[Any]], list[dict[str, str | dict[str, str]]]],
    mocker: MockerFixture,
) -> None:
    report_generator = ReportGenerator()
    aggregate_units_return: tuple[str, dict[str, str]] = ("dummy_units", {"mock_units_log": "mock_units_msg"})

    mocker.patch.object(
        report_generator, "_get_horizontal_first_value", return_value=filter_content["horizontal_first"]
    )
    mocker.patch.object(
        report_generator, "_handle_aggregation", return_value=(mock_vertical_agg, {"mock_log": "mock_log_msg"})
    )
    if mock_horizontal_agg is not None:
        mocker.patch.object(report_generator, "_apply_horizontal_aggregation", return_value=mock_horizontal_agg)

    if mock_vertical_agg is not None:
        mocker.patch.object(report_generator, "_apply_vertical_aggregation", return_value=mock_vertical_agg)
        mocker.patch.object(report_generator, "_aggregate_units", return_value=aggregate_units_return)

    with patch.dict("RUFAS.report_generator.AGGREGATION_FUNCTIONS", {"sum": sum}):
        result = report_generator._handle_horizontal_and_vertical_aggregations(
            aggregate_report, horizontal_agg_key, vertical_agg_key, filter_content
        )

    assert result == expected_output


@pytest.mark.parametrize(
    "filter_content, expected_horizontal, expected_vertical, expected_exception",
    [
        # Test with valid horizontal and vertical keys
        (
            {"horizontal_aggregation": "sum", "vertical_aggregation": "average"},
            "sum",
            "average",
            None,
        ),
        # Test with valid horizontal key and no vertical key
        ({"horizontal_aggregation": "product"}, "product", None, None),
        # Test with no horizontal key and valid vertical key
        ({"vertical_aggregation": "division"}, None, "division", None),
        # Test with empty filter content
        ({}, None, None, None),
    ],
)
def test_extract_and_check_aggregation_keys(
    filter_content: Dict[str, Any],
    expected_horizontal: str | None,
    expected_vertical: str | None,
    expected_exception: Type[Exception],
    mocker: MockerFixture,
) -> None:
    """
    Unit test for _extract_and_check_aggregation_keys() method in report_generator.py file.
    """

    # Arrange
    mock_time = mocker.MagicMock()
    report_generator = ReportGenerator(time=mock_time)

    # Act and assert
    if expected_exception:
        with pytest.raises(expected_exception):
            report_generator._extract_aggregation_keys(filter_content)
    else:
        (
            horizontal_key,
            vertical_key,
        ) = report_generator._extract_aggregation_keys(filter_content)
        assert horizontal_key == expected_horizontal
        assert vertical_key == expected_vertical


@pytest.mark.parametrize(
    "references, reports, expected_exception, expected_message",
    [
        # All references are present
        (["ref1", "ref2"], {"ref1": {}, "ref2": {}}, None, None),
        # One reference is missing
        (
            ["ref1", "ref2"],
            {"ref1": {}},
            KeyError,
            "Missing referenced reports matching the following pattern(s): ref2",
        ),
        # Multiple references are missing
        (
            ["ref1", "ref2", "ref3"],
            {"ref1": {}},
            KeyError,
            "Missing referenced reports matching the following pattern(s): ref2, ref3",
        ),
        # Reports dictionary is empty
        (["ref1"], {}, KeyError, "Missing referenced reports matching the following pattern(s): ref1"),
        # Regex match one reference
        (["ref\\d"], {"ref1": {}}, None, None),
        # Regex match multiple references
        (["ref\\d"], {"ref2": {}, "ref3": {}}, None, None),
        # Regex match none
        (
            ["ref\\d+"],
            {"report1": {}, "report2": {}},
            KeyError,
            r"Missing referenced reports matching the following pattern(s): ref\\d+",
        ),
        # Complex regex pattern
        (["ref[1-3]", "report\\d{2}"], {"ref1": {}, "ref2": {}, "report01": {}}, None, None),
    ],
)
def test_check_for_missing_references(
    mocker: MockerFixture,
    references: List[str],
    reports: Dict[str, Dict[str, Any]],
    expected_exception: Optional[Type[Exception]],
    expected_message: Optional[str],
) -> None:
    """
    Unit test for _check_for_missing_references static method in report_generator.py file.
    """

    # Arrange
    mocker.patch("RUFAS.report_generator.ReportGenerator.__init__", return_value=None)
    mock_time = mocker.MagicMock()
    report_generator = ReportGenerator(time=mock_time)
    report_generator.reports = reports

    if expected_exception:
        # Act and assert
        with pytest.raises(expected_exception) as excinfo:
            report_generator._check_for_missing_references(references)
        assert isinstance(expected_message, str) and expected_message in str(excinfo.value)
    else:
        # Act
        report_generator._check_for_missing_references(references)


@pytest.mark.parametrize(
    "regex_patterns, expected_matched_reports",
    [
        # Match single report
        (["report1"], {"report1": {"data": []}}),
        # Match multiple reports with simple pattern
        (["report\\d"], {"report1": {"data": []}, "report2": {"data": []}}),
        # Match multiple reports with complex pattern
        (["report[12]"], {"report1": {"data": []}, "report2": {"data": []}}),
        # No match
        (["unmatched"], {}),
        # Partial match not included
        (["report"], {}),
        # Match with special characters in report names
        (["special_report-\\d"], {"special_report-1": {"data": []}}),
    ],
)
def test_get_reports_by_regex(
    regex_patterns: List[str], expected_matched_reports: Dict[str, Dict[str, List[Any]]], mocker: MockerFixture
) -> None:
    """
    Unit test for _get_reports_by_regex() method in report_generator.py file.
    """

    # Arrange
    reports: Dict[str, Dict[str, List[Any]]] = {
        "report1": {"data": []},
        "report2": {"data": []},
        "special_report-1": {"data": []},
    }
    mock_time = mocker.MagicMock()
    report_generator = ReportGenerator(time=mock_time)
    report_generator.reports = reports

    # Act
    matched_reports = report_generator._get_reports_by_regex(regex_patterns)

    # Assert
    assert matched_reports == expected_matched_reports


@pytest.mark.parametrize(
    "report_name, reports, expected_name, timestamp_return_value",
    [
        # Case when the name is not in reports
        ("report1", {}, "report1", "2023-01-01"),
        # Case when the name is in reports and a timestamp is appended
        ("report1", {"report1": {}}, "report1_2023-01-01", "2023-01-01"),
        # Case when the name is None
        (None, {}, "untitled_2023-01-01", "2023-01-01"),
        # Case when the name is empty
        ("", {}, "", "2023-01-01"),
    ],
)
def test_ensure_unique_report_name_with_timestamp(
    mocker: MockerFixture,
    report_name: str,
    reports: Dict[str, Dict[str, Any]],
    expected_name: str,
    timestamp_return_value: str,
) -> None:
    """
    Unit test for _ensure_unique_report_name_with_timestamp method in report_generator.py file.
    """

    # Arrange
    mocker.patch("RUFAS.report_generator.ReportGenerator.__init__", return_value=None)
    mock_time = mocker.MagicMock()
    report_generator = ReportGenerator(time=mock_time)
    report_generator.reports = reports
    mocker.patch("RUFAS.util.Utility.get_timestamp", return_value=timestamp_return_value)

    # Act
    result = report_generator._ensure_unique_report_name_with_timestamp(report_name)

    # Assert
    assert result == expected_name


@pytest.mark.parametrize(
    "filter_content, filtered_pool, reports, reference_exception, "
    "perform_aggregations_exception, expected_report_columns, expected_log_messages,"
    "expected_get_reports_by_regex_calls",
    [
        # Standard report generation
        (
            {"name": "standard_report", "filters": ["some_filter"]},
            {"some_filter": [1, 2, 3]},
            {},
            None,
            None,
            {"standard_report": {"values": [1, 2, 3]}},
            ["Start generating individual report: standard_report"],
            0,
        ),
        # Report with name as an empty string
        (
            {"name": "", "filters": ["some_filter"]},
            {"some_filter": [1, 2, 3]},
            {},
            None,
            None,
            {"some_filter": {"values": [1, 2, 3]}},
            ["Start generating individual report: "],
            0,
        ),
        # Report with cross-references
        (
            {"name": "report_with_references", "filters": ["some_filter"], "cross_references": ["ref1"]},
            {"some_filter": [1, 2, 3]},
            {"ref1": {"values": [4, 5, 6]}},
            None,
            None,
            {
                "ref1": {"values": [4, 5, 6]},
                "report_with_references_some_filter": {"values": [1, 2, 3]},
                "report_with_references_ref1": {"values": [4, 5, 6]},
            },
            ["Start generating individual report: report_with_references"],
            1,
        ),
        # Report generation with missing cross-references
        (
            {"name": "error_report", "cross_references": ["missing_ref"]},
            {},
            {"ref": {"values": [1, 2, 3]}},
            KeyError,
            None,
            None,
            [
                "Start generating individual report: error_report",
                "Error generating report (error_report) => KeyError: ",
            ],
            0,
        ),
        # Report generation with error in _perform_aggregations
        (
            {"name": "error_report", "filters": ["some_filter"]},
            {"some_data_key": [1, 2, 3]},
            {},
            None,
            ValueError,
            None,
            [
                "Start generating individual report: error_report",
                "Error generating report (error_report) => ValueError: ",
            ],
            0,
        ),
        # Report with graph_details, without enable_graph_and_report - tests graph_data
        # creation and filtering reports by exclusion
        (
            {
                "name": "graph_report",
                "filters": ["graph_filter"],
                "graph_details": {"type": "plot", "metadata_prefix": "dummy_prefix", "graphics_dir": "dummy_dir"},
            },
            {"graph_filter": [7, 8, 9]},
            {},
            None,
            None,
            {},
            ["Start generating individual report: graph_report", "Prepared graph data for report: graph_report"],
            0,
        ),
        # Report with both graph_details and enable_graph_and_report set - tests enabling both graph and report data
        (
            {
                "name": "full_feature_report",
                "filters": ["full_feature_filter"],
                "graph_details": {"type": "plot", "metadata_prefix": "dummy_prefix", "graphics_dir": "dummy_dir"},
                "graph_and_report": True,
            },
            {"full_feature_filter": [10, 11, 12]},
            {},
            None,
            None,
            {"full_feature_report": {"values": [10, 11, 12]}},
            [
                "Start generating individual report: full_feature_report",
                "Prepared graph data for report: full_feature_report",
            ],
            0,
        ),
        # Report with enable_graph_and_report set but without graph_details
        # tests warning log for missing graph_details
        (
            {
                "name": "graph_report_missing_details",
                "filters": ["missing_graph_filter"],
                "graph_and_report": True,
            },
            {"missing_graph_filter": [13, 14, 15]},
            {},
            None,
            None,
            {"graph_report_missing_details": {"values": [13, 14, 15]}},
            [
                "Start generating individual report: graph_report_missing_details",
                "Request to graph and report data not fulfilled - no graph_details present in report filter file.",
            ],
            0,
        ),
        # Existing test cases with added last parameter 'expected_get_reports_by_regex_calls'
        # Example for the report with cross-references test case:
        (
            {"name": "report_with_references", "filters": ["some_filter"], "cross_references": ["ref1"]},
            {"some_filter": [1, 2, 3]},
            {"ref1": {"values": [4, 5, 6]}},
            None,
            None,
            {
                "ref1": {"values": [4, 5, 6]},
                "report_with_references_some_filter": {"values": [1, 2, 3]},
                "report_with_references_ref1": {"values": [4, 5, 6]},
            },
            ["Start generating individual report: report_with_references"],
            1,
        ),
        # Test case for "data_significant_digits" in filter
        (
            {"name": "test_report", "filters": ["filter1"], "data_significant_digits": 2},
            {"filter1": [1.23456789, 2.3456789, 3.456789]},
            {},
            None,
            None,
            {"test_report": {"values": [1.23, 2.35, 3.46]}},
            ["Start generating individual report: test_report"],
            0,
        ),
    ],
)
def test_generate_report(
    filter_content: dict[str, Any],
    filtered_pool: dict[str, Any],
    reports: dict[str, dict[str, list[Any]]],
    reference_exception: Optional[Type[BaseException]],
    perform_aggregations_exception: Optional[Type[BaseException]],
    expected_report_columns: dict[str, dict[str, list[Any]]],
    expected_log_messages: list[str],
    expected_get_reports_by_regex_calls: int,
    mocker: MockerFixture,
) -> None:
    """
    Unit test for the generate_report method in the ReportGenerator class.
    """

    # Arrange
    mocker.patch("RUFAS.report_generator.ReportGenerator.__init__", return_value=None)
    mock_time = mocker.MagicMock()
    report_generator = ReportGenerator(time=mock_time)
    report_generator.reports = reports
    mocker.patch.object(report_generator, "_ensure_unique_report_name_with_timestamp", side_effect=lambda name: name)
    mocker.patch.object(
        report_generator,
        "_check_for_missing_references",
        side_effect=reference_exception if reference_exception else None,
    )
    mocker.patch.object(
        report_generator,
        "_prepare_report_data_to_be_graphed",
        side_effect=lambda graph_data, filter_content, report_name: [
            {
                "message": f"Prepared graph data for report: {report_name}",
                "info_map": {},
            }
        ],
    )
    mocker.patch("RUFAS.report_generator.Utility.filter_dictionary", return_value=expected_report_columns)
    if perform_aggregations_exception:
        mocker.patch.object(
            report_generator,
            "_perform_aggregations",
            side_effect=perform_aggregations_exception,
        )
    elif not reference_exception:
        mocker.patch.object(
            report_generator,
            "_perform_aggregations",
            return_value=(
                {fltr: filtered_pool[fltr] for fltr in filter_content["filters"]}
                | {ref: reports[ref]["values"] for ref in filter_content.get("cross_references", [])},
                [],
                False,
            ),
        )

    get_reports_by_regex_spy = mocker.spy(report_generator, "_get_reports_by_regex")

    # Act
    event_logs = report_generator.generate_report(filter_content, filtered_pool)

    # Assert
    if not reference_exception and not perform_aggregations_exception:
        assert report_generator.reports == expected_report_columns
    log_messages = [log["message"] for log in event_logs]
    for expected_message in expected_log_messages:
        assert expected_message in log_messages

    assert get_reports_by_regex_spy.call_count == expected_get_reports_by_regex_calls


def test_prepare_report_data_to_be_graphed(mocker: MockerFixture) -> None:
    """
    Unit test for the _prepare_report_data_to_be_graphed method in the ReportGenerator class.
    """

    # Arrange
    mock_time = mocker.MagicMock()
    report_generator = ReportGenerator(time=mock_time)
    individual_report_name = "test_report"
    graph_data = {"some_data_key": [1, 2, 3]}
    filter_content = {
        "name": "example_report",
        "filters": ["filter1", "filter2"],
        "graph_details": {
            "metadata_prefix": "prefix",
            "graphics_dir": "dir",
            "other_details": "details",
            "produce_graphics": True,
            "is_aggregated_report_data": True,
        },
    }
    produce_graphics = True

    mock_generate_graph = mocker.patch.object(
        GraphGenerator, "generate_graph", return_value=[{"status": "success", "message": "Graph generated"}]
    )
    graph_event_log = report_generator._prepare_report_data_to_be_graphed(
        graph_data, filter_content, individual_report_name
    )

    mock_generate_graph.assert_called_once_with(
        graph_data,
        {
            "metadata_prefix": "prefix",
            "other_details": "details",
            "produce_graphics": True,
            "title": "example_report",
            "filters": ["filter1", "filter2"],
            "is_aggregated_report_data": True,
        },
        individual_report_name,
        "dir",
        produce_graphics,
    )

    assert graph_event_log == [
        {
            "status": "success",
            "message": "Graph generated",
        }
    ], "Graph event log did not match expected output"


def test_report_generator_init(mocker: MockerFixture) -> None:
    """
    Unit test for the __init__ method of ReportGenerator class in report_generator.py file.
    """

    # Arrange
    expected_reports: Dict[str, Dict[str, List[Any]]] = {}
    mock_time = mocker.MagicMock()

    # Act
    report_generator = ReportGenerator(time=mock_time)

    # Assert
    assert report_generator.reports == expected_reports


def test_clear_reports(mocker: MockerFixture) -> None:
    """
    Unit test for the clear_reports method of ReportGenerator class in report_generator.py file.
    """

    # Arrange
    mock_time = mocker.MagicMock()
    report_generator = ReportGenerator(time=mock_time)
    report_generator.reports = {"report1": {}, "report2": {}}

    # Act
    report_generator.clear_reports()

    # Assert
    assert report_generator.reports == {}


@pytest.mark.parametrize(
    "filter_content, expected_result, expected_exception",
    [
        ({"horizontal_first": True}, True, None),
        ({"horizontal_first": False}, False, None),
        ({}, False, None),
        ({"horizontal_first": "true"}, None, ValueError),
        ({"horizontal_first": "false"}, None, ValueError),
        ({"horizontal_first": 1}, None, ValueError),
        ({"horizontal_first": None}, False, None),
    ],
)
def test_get_horizontal_first_value(
    filter_content: Dict[str, Any],
    expected_result: bool,
    expected_exception: Exception | None,
) -> None:
    """
    Unit test for the _get_horizontal_first_value method of ReportGenerator class in report_generator.py file.
    """

    # Arrange
    report_generator = ReportGenerator()

    # Act & Assert
    if expected_exception:
        with pytest.raises(ValueError) as exc_info:
            report_generator._get_horizontal_first_value(filter_content)
        assert str(exc_info.value) == (
            f"The value of 'horizontal_first' in the report filter should be a boolean. "
            f"Value provided: {repr(filter_content['horizontal_first'])} "
            f"(type {type(filter_content['horizontal_first'])})"
        )
    else:
        result = report_generator._get_horizontal_first_value(filter_content)
        assert result == expected_result


@pytest.mark.parametrize(
    "input_data, expected_output",
    [
        (
            {"temperature": {"info_maps": [{"units": "Celsius"}], "values": [23, 24, 25]}},
            {"temperature (Celsius)": {"info_maps": [{"units": "Celsius"}], "values": [23, 24, 25]}},
        ),
        (
            {"pressure": {"info_maps": [{"units": {"pressure": "Pascal"}}], "values": [101325, 101300]}},
            {"pressure (Pascal)": {"info_maps": [{"units": {"pressure": "Pascal"}}], "values": [101325, 101300]}},
        ),
        (
            {"humidity": {"info_maps": [{"units": "percent"}], "values": [80, 75, 70]}},
            {"humidity (percent)": {"info_maps": [{"units": "percent"}], "values": [80, 75, 70]}},
        ),
        ({"humidity": {"values": [80, 75, 70]}}, {"humidity": {"values": [80, 75, 70]}}),
    ],
)
def test_add_var_units(
    input_data: dict[str, dict[str, list[Any]]], expected_output: dict[str, dict[str, list[Any]]]
) -> None:
    report_generator = ReportGenerator()
    assert report_generator._add_var_units(input_data) == expected_output


@pytest.mark.parametrize(
    "report_data, aggregator, simplify_units, expected_output, raises_error",
    [
        ({"temperature (Celsius)": [23.0, 24.0, 25.0]}, sum, False, ("Celsius", {}), False),
        ({"pressure (Pascal)": [101325.0, 101300.0]}, sum, False, ("Pascal", {}), False),
        ({"wind_speed (m/s)": [10.0, 12.0, 15.0]}, sum, False, ("m/s", {}), False),
        ({}, sum, False, ("", {}), True),
    ],
)
def test_aggregate_units(
    report_data: dict[str, list[float]],
    aggregator: Callable[[list[float]], float] | Callable[[list[float]], float | None],
    simplify_units: bool,
    expected_output: tuple[str | Any, dict[str, str | dict[str, str]]],
    raises_error: bool,
) -> None:
    report_generator = ReportGenerator()
    if raises_error:
        with pytest.raises(ValueError):
            report_generator._aggregate_units(report_data, aggregator, False)
    else:
        assert report_generator._aggregate_units(report_data, aggregator, simplify_units) == expected_output


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
    ],
)
def test_normalize_constant_name(input_name: str, expected_output: str) -> None:
    """
    Test the _normalize_constant_name method to ensure it normalizes the constant name
    by converting it to lowercase and removing underscores and spaces.
    """
    report_generator = ReportGenerator()
    assert report_generator._normalize_constant_name(input_name) == expected_output


@pytest.mark.parametrize(
    "aggregator, data, key, expected_result, expected_log",
    [
        # Valid data: normal floats
        (sum, [1.0, 2.0, 3.0], "valid_key", 6.0, {}),
        # None in data
        (
            sum,
            [1.0, None, 3.0],
            "none_key",
            None,
            {
                "error": "ReportGenerator aggregation error",
                "message": "Encountered unaggregatable values in variable(s): none_key. Returning None instead.",
                "info_map": {"class": "ReportGenerator", "function": "_handle_aggregation"},
            },
        ),
        # NaN in data
        (
            sum,
            [1.0, float("nan"), 3.0],
            "nan_key",
            None,
            {
                "error": "ReportGenerator aggregation error",
                "message": "Encountered unaggregatable values in variable(s): nan_key. Returning None instead.",
                "info_map": {"class": "ReportGenerator", "function": "_handle_aggregation"},
            },
        ),
        # Empty list
        (sum, [], "empty_key", 0, {}),
        # Aggregator raises error
        (
            lambda x: x[0] / 0,
            [1.0, 2.0, 3.0],
            "key",
            None,
            {
                "error": "ReportGenerator aggregation error",
                "message": "Error during aggregation of key data: float division by zero, returning None instead.",
                "info_map": {"class": "ReportGenerator", "function": "_handle_aggregation"},
            },
        ),
        # NumPy floats — valid
        (sum, [np.float64(1.0), np.float64(2.0), np.float64(3.0)], "np_float_key", 6.0, {}),
        # NumPy int — valid
        (sum, [np.int64(1), np.int64(2), np.int64(3)], "np_int_key", 6, {}),
        # Complex — invalid
        (
            sum,
            [1.0, 2.0, complex(1, 1)],
            "complex_key",
            None,
            {
                "error": "ReportGenerator aggregation error",
                "message": "Encountered unaggregatable values in variable(s): complex_key. Returning None instead.",
                "info_map": {"class": "ReportGenerator", "function": "_handle_aggregation"},
            },
        ),
        # String — invalid
        (
            sum,
            [1.0, "a", 3.0],
            "string_key",
            None,
            {
                "error": "ReportGenerator aggregation error",
                "message": "Encountered unaggregatable values in variable(s): string_key. Returning None instead.",
                "info_map": {"class": "ReportGenerator", "function": "_handle_aggregation"},
            },
        ),
        # Bool — valid (bool is a subclass of int)
        (sum, [True, False, 1.0], "bool_key", 2.0, {}),
    ],
)
def test_handle_aggregation(
    aggregator: Callable[[List[float]], float],
    data: list[Any],
    key: str,
    expected_result: float | None,
    expected_log: dict[str, str | dict[str, str]],
) -> None:
    report_generator = ReportGenerator()
    result, log = report_generator._handle_aggregation(aggregator, data, key)
    assert result == expected_result
    assert log == expected_log

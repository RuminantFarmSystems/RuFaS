from __future__ import annotations

from typing import Dict, List, Any, Callable

import pytest
from pytest_mock import MockerFixture

from RUFAS.report_generator import (
    average_aggregator,
    division_aggregator,
    product_aggregator,
    sd_aggregator,
    sum_aggregator,
    subtraction_aggregator,
    ReportGenerator,
    average_aggregator_with_scalar_op,
    division_aggregator_with_scalar_op,
    product_aggregator_with_scalar_op,
    sd_aggregator_with_scalar_op,
    sum_aggregator_with_scalar_op,
    AGGREGATION_FUNCTIONS_WITH_SCALAR_OP,
)


def test_average_aggregator():
    assert average_aggregator([1, 2, 3, 4, 5]) == 3
    assert average_aggregator([-1, -2, -3, -4, -5]) == -3
    assert average_aggregator([]) == 0


def test_division_aggregator():
    assert division_aggregator([100, 2, 5]) == 10
    assert division_aggregator([100, -2, 5]) == -10
    assert division_aggregator([]) is None
    assert division_aggregator([10]) is None
    assert division_aggregator([10, 0]) is None


def test_product_aggregator():
    assert product_aggregator([1, 2, 3, 4, 5]) == 120
    assert product_aggregator([-1, 2, -3, 4, -5]) == -120
    assert product_aggregator([]) == 1


def test_sd_aggregator():
    assert sd_aggregator([2, 4, 4, 4, 5, 5, 7, 9]) == pytest.approx(2)
    assert sd_aggregator([-2, -4, -4, -4, -5, -5, -7, -9]) == pytest.approx(2)
    assert sd_aggregator([]) == 0


def test_sum_aggregator():
    assert sum_aggregator([1, 2, 3, 4, 5]) == 15
    assert sum_aggregator([-1, -2, -3, -4, -5]) == -15
    assert sum_aggregator([]) == 0


def test_subtraction_aggregator():
    assert subtraction_aggregator([10, 2, 3]) == 5
    assert subtraction_aggregator([10, -2, -3]) == 15
    assert subtraction_aggregator([]) is None
    assert subtraction_aggregator([10]) is None


class MockUtility:
    @staticmethod
    def convert_list_of_dicts_to_dict_of_lists(
            data: List[Dict[str, Any]]
    ) -> Dict[str, List[Any]]:
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


def test_generate_report_vertical_then_horizontal(
        report_generator: ReportGenerator,
        sample_filtered_pool: Dict[str, Dict[str, List[Dict[str, int]]]],
):
    filter_content = {
        "variables": ["a", "b"],
        "horizontal_aggregation": "average",
        "vertical_aggregation": "sum",
        "horizontal_first": False,
    }
    assert report_generator.generate_report(sample_filtered_pool, filter_content) == [
        18
    ]


def test_generate_report_horizontal_then_vertical(
        report_generator: ReportGenerator,
        sample_filtered_pool: Dict[str, Dict[str, List[Dict[str, int]]]],
):
    filter_content = {
        "variables": ["a", "b"],
        "horizontal_aggregation": "sum",
        "vertical_aggregation": "average",
        "horizontal_first": True,
    }
    assert report_generator.generate_report(sample_filtered_pool, filter_content) == [9]


def test_generate_report_only_horizontal(
        report_generator: ReportGenerator,
        sample_filtered_pool: Dict[str, Dict[str, List[Dict[str, int]]]],
):
    filter_content = {
        "variables": ["a", "b"],
        "horizontal_aggregation": "sum",
    }
    assert report_generator.generate_report(sample_filtered_pool, filter_content) == [
        3,
        7,
        11,
        15,
    ]


def test_generate_report_only_vertical(
        report_generator: ReportGenerator,
        sample_filtered_pool: Dict[str, Dict[str, List[Dict[str, int]]]],
):
    filter_content = {
        "variables": ["a", "b"],
        "vertical_aggregation": "average",
    }
    assert report_generator.generate_report(sample_filtered_pool, filter_content) == [
        4,
        5,
    ]


def test_generate_report_no_aggregation(
        report_generator: ReportGenerator,
        sample_filtered_pool: Dict[str, Dict[str, List[Dict[str, int]]]],
):
    filter_content = {
        "variables": ["a", "b"],
    }
    with pytest.raises(ValueError):
        report_generator.generate_report(sample_filtered_pool, filter_content)


def test_generate_report_invalid_empty_data(report_generator: ReportGenerator) -> None:
    filtered_pool: Dict[str, Dict[str, List[Any]]] = {}
    filter_content: Dict[str, Any] = {
        "variables": ["a", "b"],
        "horizontal_aggregation": "sum",
        "vertical_aggregation": "average",
    }
    with pytest.raises(ValueError):
        report_generator.generate_report(filtered_pool, filter_content)


def test_prepare_report_data_valid_list(report_generator: ReportGenerator) -> None:
    filtered_pool: Dict[str, Dict[str, List[int]]] = {
        "data1": {"values": [1, 2, 3, 4]},
        "data2": {"values": [5, 6, 7, 8]},
    }
    assert report_generator._prepare_report_data(filtered_pool, None, 1, 3) == {
        "data1": [2, 3],
        "data2": [6, 7],
    }


def test_prepare_report_data_valid_dict(
        report_generator: ReportGenerator,
        sample_filtered_pool: Dict[str, Dict[str, List[Dict[str, int]]]],
) -> None:
    actual = report_generator._prepare_report_data(
        sample_filtered_pool, ["a", "b"], 1, 3
    )
    expected = {"a": [3, 7], "b": [4, 8]}
    assert actual == expected


def test_prepare_report_data_invalid_no_variables(
        report_generator: ReportGenerator,
        sample_filtered_pool: Dict[str, Dict[str, List[Dict[str, int]]]],
) -> None:
    with pytest.raises(KeyError):
        report_generator._prepare_report_data(sample_filtered_pool, None, 0, 0)


def test_prepare_report_data_aggregate_values(
        report_generator: ReportGenerator,
        sample_filtered_pool: Dict[str, Dict[str, List[Dict[str, int]]]],
) -> None:
    actual = report_generator._prepare_report_data(
        sample_filtered_pool, ["a", "b"], 0, None
    )
    expected = {
        "a": [1, 3, 5, 7],
        "b": [2, 4, 6, 8],
    }
    assert actual == expected


def test_generate_report_with_invalid_horizontal_order(
        report_generator: ReportGenerator,
        sample_filtered_pool: Dict[str, Dict[str, List[Dict[str, int]]]],
):
    filter_content = {
        "variables": ["a", "b"],
        "horizontal_order": ["invalid_key", "b"],
        "horizontal_aggregation": "average",
        "vertical_aggregation": "sum",
        "horizontal_first": True,
    }
    with pytest.raises(KeyError):
        report_generator.generate_report(sample_filtered_pool, filter_content)


def test_generate_report_with_valid_horizontal_order(
        report_generator: ReportGenerator,
        sample_filtered_pool: Dict[str, Dict[str, List[Dict[str, int]]]],
):
    filter_content = {
        "variables": ["a", "b"],
        "horizontal_aggregation": "division",
        "vertical_aggregation": "sum",
        "horizontal_first": True,
    }
    filter_content["horizontal_order"] = ["a", "b"]
    assert report_generator.generate_report(sample_filtered_pool, filter_content) == [
        2.9583333333333335
    ]
    filter_content["horizontal_order"] = ["b", "a"]
    assert report_generator.generate_report(sample_filtered_pool, filter_content) == [
        5.676190476190476
    ]


@pytest.mark.parametrize(
    "input_list, target_length, pad_value, expected", [
        # Normal cases
        ([1, 2, 3], 5, 0, [1, 2, 3, 0, 0]),

        # Padding an empty list
        ([], 3, 'a', ['a', 'a', 'a']),

        # No padding needed (list already at target length)
        ([1, 2], 2, 9, [1, 2]),

        # Padding with None
        ([1], 3, None, [1, None, None]),

        # List longer than target length (no padding)
        ([1, 2, 3], 1, 0, [1, 2, 3]),

        # empty list, zero length
        ([], 0, 0, []),
    ])
def test_pad_list_with_value(input_list: List[Any],
                             target_length: int,
                             pad_value: Any,
                             expected: List[Any]
                             ) -> None:
    """
    Unit test for _pad_list_with_value() static method in report_generator.py file.
    """

    # Act
    ReportGenerator._pad_list_with_value(input_list, target_length, pad_value)

    # Assert
    assert input_list == expected


@pytest.mark.parametrize(
    "input_list, target_length, expected", [
        # Normal case: padding required
        ([1, 2], 5, [1, 2, 1, 2, 1]),

        # List already at target length
        ([1, 2, 3], 3, [1, 2, 3]),

        # List longer than target length: no padding
        ([1, 2, 3], 2, [1, 2, 3]),

        # Empty list
        ([], 4, []),

        # Padding to zero length
        ([1, 2], 0, [1, 2]),

        # Cycling multiple times
        ([1, 2, 3], 10, [1, 2, 3, 1, 2, 3, 1, 2, 3, 1])
    ])
def test_pad_list_with_cycle(input_list: List[float], target_length: int, expected: List[float]) -> None:
    """
    Unit test for _pad_list_with_cycle() static method in report_generator.py file.
    """

    # Act
    ReportGenerator._pad_list_with_cycle(input_list, target_length)

    # Assert
    assert input_list == expected


@pytest.mark.parametrize(
    "input_data, padding_config, expected", [
        # No padding ('none' method)
        ([[1, 2], [1, 2, 3]], {"method": "none"}, [[1, 2], [1, 2, 3]]),

        # Padding with a custom value
        ([[1], [1, 2]], {"method": "custom", "value": 0}, [[1, 0], [1, 2]]),

        # Padding with cycle
        ([[1], [1, 2]], {"method": "cycle"}, [[1, 1], [1, 2]]),

        # First element padding
        ([[1, 2], [3]], {"method": "first"}, [[1, 2], [3, 3]]),

        # Last element padding
        ([[1, 2], [3]], {"method": "last"}, [[1, 2], [3, 3]]),

        # Average padding
        ([[1, 2], [3, 4, 5]], {"method": "avg"}, [[1, 2, 1.5], [3, 4, 5]]),

        # Minimum value padding
        ([[1, 2], [3, 4, 5]], {"method": "min"}, [[1, 2, 1], [3, 4, 5]]),

        # Maximum value padding
        ([[1, 2], [3, 4, 5]], {"method": "max"}, [[1, 2, 2], [3, 4, 5]]),

        # Zero padding
        ([[1, 2], [3]], {"method": "zero"}, [[1, 2], [3, 0]]),

        # One padding
        ([[1, 2], [3]], {"method": "one"}, [[1, 2], [3, 1]]),

        # Null padding
        ([[1, 2], [3]], {"method": "null"}, [[1, 2], [3, None]]),

        # Empty list
        ([[], [1, 2]], {"method": "first"}, [[None, None], [1, 2]]),

        # All lists already at max length
        ([[1, 2], [3, 4]], {"method": "first"}, [[1, 2], [3, 4]]),
    ])
def test_apply_padding(input_data: List[List[float]], padding_config: Dict[str, Any],
                       expected: List[List[float]]) -> None:
    """
    Unit test for _apply_padding() static method in report_generator.py file.
    """

    # Act
    ReportGenerator._apply_padding(input_data, padding_config)

    # Assert
    assert input_data == expected


@pytest.mark.parametrize(
    "report_data, aggregator, scalar, operation, expected", [
        # Tests with sum aggregator and addition operation
        ({"a": [1, 2], "b": [3, 4]}, sum_aggregator_with_scalar_op, 10, "sum", [23, 27]),
        ({"a": [1, 2], "b": [3, 4]}, sum_aggregator_with_scalar_op, 5, "subtraction", [-7, -3]),

        # Tests with product aggregator and multiply operation
        ({"a": [1, 2], "b": [3, 4]}, product_aggregator_with_scalar_op, 2, "product", [8, 48]),
        ({"a": [1, 2], "b": [3, 4]}, product_aggregator_with_scalar_op, 2, "division", [0.5, 3.0]),

        # Tests with empty data
        ({"a": [], "b": []}, sum_aggregator_with_scalar_op, 0, "sum", [0, 0]),

        # Tests with None values in data
        ({"a": [1, None], "b": [None, 4]}, sum_aggregator_with_scalar_op, 5, "sum", [6, 9]),

        # Tests with average aggregator
        ({"a": [1, 2, 3], "b": [4, 5, 6]}, average_aggregator_with_scalar_op, 10, "sum", [12.0, 15.0]),
        ({"a": [10, 20], "b": [30, 40]}, average_aggregator_with_scalar_op, 5, "product", [75.0, 175.0]),

        # Tests with division aggregator
        ({"a": [8, 4], "b": [2, 1]}, division_aggregator_with_scalar_op, 2, "exponent", [4.0, 4.0]),
        ({"a": [100, 50], "b": [25, 10]}, division_aggregator_with_scalar_op, 10, "subtraction", [2.25, None]),

        # Tests with standard deviation aggregator
        ({"a": [10, 12, 23, 23], "b": [17, 15, 22, 20]}, sd_aggregator_with_scalar_op, 2, "sum",
         [6.041522986797286, 2.692582403567252]),
        ({"a": [10, 12, 23, 23], "b": [17, 15, 22, 20]}, sd_aggregator_with_scalar_op, 2, "division",
         [3.020761493398643, 1.346291201783626]),
    ])
def test_apply_vertical_aggregation(report_data: Dict[str, List[float]],
                                    aggregator: Callable[[List[float], float, str], float],
                                    scalar: float, operation: str, expected: List[float]) -> None:
    """
    Unit test for _apply_vertical_aggregation() static method in report_generator.py file.
    """

    # Act
    result = ReportGenerator._apply_vertical_aggregation(report_data, aggregator, scalar, operation)

    # Assert
    assert result == expected


@pytest.mark.parametrize(
    "report_data, loop_list, aggregator, scalar, operation, expected", [
        # Tests with sum aggregation
        ({"a": [1, 2], "b": [3, 4]}, ['a', 'b'], sum_aggregator_with_scalar_op, 10, "sum", [24, 26]),
        ({"a": [1, 2], "b": [3, 4]}, ['a', 'b'], sum_aggregator_with_scalar_op, 5, "subtraction", [-6, -4]),

        # Tests with product aggregation
        ({"a": [1, 2], "b": [3, 4]}, ['a', 'b'], product_aggregator_with_scalar_op, 2, "product", [12, 32]),
        ({"a": [1, 2], "b": [3, 4]}, ['a', 'b'], product_aggregator_with_scalar_op, 2, "division", [0.75, 2.0]),

        # Tests with average aggregation
        ({"a": [1, 3], "b": [2, 4]}, ['a', 'b'], average_aggregator_with_scalar_op, 5, "sum", [6.5, 8.5]),
        ({"a": [1, 3], "b": [2, 4]}, ['a', 'b'], average_aggregator_with_scalar_op, 5, "subtraction", [-3.5, -1.5]),

        # Tests with division aggregation
        ({"a": [8, 16], "b": [4, 2]}, ['a', 'b'], division_aggregator_with_scalar_op, 2, "division", [2.0, 8.0]),
        ({"a": [8, 16], "b": [4, 2]}, ['a', 'b'], division_aggregator_with_scalar_op, 2, "exponent", [4.0, 64.0]),

        # Tests with standard deviation aggregation
        ({"a": [10, 10], "b": [20, 20]}, ['a', 'b'], sd_aggregator_with_scalar_op, 5, "subtraction",
         [5.0, 5.0]),
        ({"a": [10, 10], "b": [20, 20]}, ['a', 'b'], sd_aggregator_with_scalar_op, 5, "division",
         [1.0, 1.0]),

        # Tests with division by zero
        ({"a": [1, 2], "b": [0, 0]}, ['a', 'b'], division_aggregator_with_scalar_op, 0, "division", [None, None]),

        # Exponent operation with product aggregator
        ({"a": [2, 3], "b": [4, 5]}, ['a', 'b'], product_aggregator_with_scalar_op, 2, "exponent", [64, 225]),
    ])
def test_apply_horizontal_aggregation(report_data: Dict[str, List[float]], loop_list: List[str],
                                      aggregator: Callable[[List[float], float, str], float], scalar: float,
                                      operation: str, expected: List[float]) -> None:
    """
    Unit test for _apply_horizontal_aggregation() static method in report_generator.py file.
    """

    # Act
    result = ReportGenerator._apply_horizontal_aggregation(report_data, loop_list, aggregator, scalar, operation)

    # Assert
    assert result == expected


@pytest.mark.parametrize(
    "report_data, filter_content, expected_result, expected_call", [
        # Valid horizontal aggregation with sum
        (
                {"a": [1, 2], "b": [3, 4]},
                {
                    "horizontal_aggregation": "sum",
                    "horizontal_order": ["a", "b"],
                    "horizontal_constant": 10,
                    "horizontal_scalar_operation": "sum"
                },
                [24, 26],
                True
        ),
        # No horizontal aggregation specified
        (
                {"a": [1, 2], "b": [3, 4]},
                {},  # No horizontal aggregation key
                None,
                False
        ),
        # Unsupported horizontal aggregation type
        (
                {"a": [1, 2]},
                {"horizontal_aggregation": "unsupported"},
                ValueError,
                False
        ),
    ]
)
def test_process_horizontal_aggregation(report_data: Dict[str, List[float]],
                                        filter_content: Dict[str, Any],
                                        expected_result: Any,
                                        expected_call: bool,
                                        mocker: MockerFixture) -> None:
    """
    Unit test for the _process_horizontal_aggregation method of ReportGenerator in report_generator.py file.
    """

    # Arrange
    patch_for_apply_horizontal_agg = mocker.patch.object(
        ReportGenerator,
        '_apply_horizontal_aggregation',
        return_value=expected_result if not isinstance(expected_result, Exception) else None
    )

    rg = ReportGenerator()

    # Act and assert
    if expected_result is ValueError:
        with pytest.raises(ValueError):
            rg._process_horizontal_aggregation(report_data, filter_content)
    else:
        result = rg._process_horizontal_aggregation(report_data, filter_content)

        assert result == expected_result

        if expected_call:
            patch_for_apply_horizontal_agg.assert_called_once_with(
                report_data,
                filter_content.get("horizontal_order", report_data.keys()),
                AGGREGATION_FUNCTIONS_WITH_SCALAR_OP[filter_content["horizontal_aggregation"]],
                filter_content.get("horizontal_constant", 1),
                filter_content.get("horizontal_scalar_operation", "product")
            )
        else:
            patch_for_apply_horizontal_agg.assert_not_called()


@pytest.mark.parametrize(
    "report_data, filter_content, expected_result, expected_call", [
        # Valid vertical aggregation with sum
        (
                {"a": [1, 2], "b": [3, 4]},
                {
                    "vertical_aggregation": "sum",
                    "vertical_order": ["a", "b"],
                    "vertical_constant": 10,
                    "vertical_scalar_operation": "sum"
                },
                [24, 26],
                True
        ),
        # No vertical aggregation specified
        (
                {"a": [1, 2], "b": [3, 4]},
                {},
                None,
                False
        ),
        # Unsupported vertical aggregation type
        (
                {"a": [1, 2]},
                {"vertical_aggregation": "unsupported"},
                ValueError,
                False
        ),
    ]
)
def test_process_vertical_aggregation(report_data: Dict[str, List[float]],
                                      filter_content: Dict[str, Any],
                                      expected_result: List[float] | None | ValueError,
                                      expected_call: bool,
                                      mocker: MockerFixture) -> None:
    """
    Unit test for the _process_vertical_aggregation method of ReportGenerator in report_generator.py file.
    """

    # Arrange
    mock_apply_agg = mocker.patch.object(
        ReportGenerator,
        '_apply_vertical_aggregation',
        return_value=expected_result if not isinstance(expected_result, Exception) else None
    )
    rg = ReportGenerator()

    # Act and assert
    if expected_result is ValueError:
        with pytest.raises(ValueError):
            rg._process_vertical_aggregation(report_data, filter_content)
    else:
        result = rg._process_vertical_aggregation(report_data, filter_content)
        assert result == expected_result

        if expected_call:
            mock_apply_agg.assert_called_once_with(
                report_data,
                AGGREGATION_FUNCTIONS_WITH_SCALAR_OP[filter_content["vertical_aggregation"]],
                filter_content.get("vertical_constant", 1),
                filter_content.get("vertical_scalar_operation", "product")
            )
        else:
            mock_apply_agg.assert_not_called()

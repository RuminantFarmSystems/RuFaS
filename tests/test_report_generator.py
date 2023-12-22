from __future__ import annotations

from typing import Dict, List, Any

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
    AGGREGATION_FUNCTIONS,
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
    assert report_generator.generate_report(sample_filtered_pool, filter_content) == {
        "ver_hor_agg": [18.0]
    }


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
    assert report_generator.generate_report(sample_filtered_pool, filter_content) == {
        "hor_ver_agg": [9.0]
    }


def test_generate_report_only_horizontal(
        report_generator: ReportGenerator,
        sample_filtered_pool: Dict[str, Dict[str, List[Dict[str, int]]]],
):
    filter_content = {
        "variables": ["a", "b"],
        "horizontal_aggregation": "sum",
    }
    assert report_generator.generate_report(sample_filtered_pool, filter_content) == {
        "hor_agg": [3, 7, 11, 15]
    }


def test_generate_report_only_vertical(
        report_generator: ReportGenerator,
        sample_filtered_pool: Dict[str, Dict[str, List[Dict[str, int]]]],
):
    filter_content = {
        "variables": ["a", "b"],
        "vertical_aggregation": "average",
    }
    assert report_generator.generate_report(sample_filtered_pool, filter_content) == {
        "ver_agg": [4.0, 5.0]
    }


def test_generate_report_no_aggregation(
        report_generator: ReportGenerator,
        sample_filtered_pool: Dict[str, Dict[str, List[Dict[str, int]]]],
):
    filter_content = {
        "variables": ["a", "b"],
    }
    assert report_generator.generate_report(sample_filtered_pool, filter_content) == {
        "a": [1, 3, 5, 7],
        "b": [2, 4, 6, 8],
    }


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
    assert report_generator.generate_report(sample_filtered_pool, filter_content) == {
        "hor_ver_agg": [2.9583333333333335]
    }
    filter_content["horizontal_order"] = ["b", "a"]
    assert report_generator.generate_report(sample_filtered_pool, filter_content) == \
           {'hor_ver_agg': [5.676190476190476]}


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
    "report_data, aggregator_key, expected", [
        # Tests with sum aggregator
        ({"a": [1, 2], "b": [3, 4]}, "sum", [3, 7]),
        ({"a": [1, 2, 3], "b": [4, 5, 6]}, "sum", [6, 15]),

        # Tests with product aggregator
        ({"a": [1, 2], "b": [3, 4]}, "product", [2, 12]),
        ({"a": [1, 2, 3], "b": [4, 5, 6]}, "product", [6, 120]),

        # Tests with average aggregator
        ({"a": [1, 2, 3], "b": [4, 5, 6]}, "average", [2.0, 5.0]),
        ({"a": [1, 2, 3, 4], "b": [5, 6, 7, 8]}, "average", [2.5, 6.5]),

        # Tests with division aggregator
        ({"a": [8, 4], "b": [2, 1]}, "division", [2.0, 2.0]),
        ({"a": [8, 4, 2], "b": [2, 1, 1]}, "division", [1.0, 2.0]),

        # Tests with standard deviation aggregator
        ({"a": [10, 12, 23, 23], "b": [17, 15, 22, 20]}, "SD", [6.041522986797286, 2.692582403567252]),
        ({"a": [10, 12, 23, 23, 23], "b": [17, 15, 22, 20, 20]}, "SD", [5.912698199637793, 2.481934729198171]),

        # Test with empty data
        ({"a": [], "b": []}, "sum", [0, 0]),

        # Test with None values in data
        ({"a": [1, None], "b": [None, 4]}, "sum", [1, 4]),
    ])
def test_apply_vertical_aggregation(report_data: Dict[str, List[float]],
                                    aggregator_key: str,
                                    expected: List[float]
                                    ) -> None:
    """
    Unit test for _apply_vertical_aggregation() static method in report_generator.py file.
    """

    # Arrange
    aggregator = AGGREGATION_FUNCTIONS[aggregator_key]

    # Act
    result = ReportGenerator._apply_vertical_aggregation(report_data, aggregator)

    # Assert
    assert result == expected


@pytest.mark.parametrize(
    "report_data, loop_list, aggregator_key, expected, expected_exception", [
        # Tests with sum aggregation
        ({"a": [1, 2], "b": [3, 4]}, ['a', 'b'], "sum", [4, 6], None),
        ({"a": [1, 2, 3], "b": [4, 5, 6]}, ['a', 'b'], "sum", [5, 7, 9], None),

        # Tests with subtraction aggregation
        ({"a": [1, 2], "b": [3, 4]}, ['a', 'b'], "subtraction", [-2, -2], None),
        ({"a": [1, 2, 3], "b": [4, 5, 6]}, ['a', 'b'], "subtraction", [-3, -3, -3], None),

        # Tests with product aggregation
        ({"a": [1, 2], "b": [3, 4]}, ['a', 'b'], "product", [3, 8], None),
        ({"a": [1, 2, 3], "b": [4, 5, 6]}, ['a', 'b'], "product", [4, 10, 18], None),

        # Tests with division aggregation
        ({"a": [1, 2], "b": [3, 4]}, ['a', 'b'], "division", [0.3333333333333333, 0.5], None),
        ({"a": [1, 2, 3], "b": [4, 5, 6]}, ['a', 'b'], "division", [0.25, 0.4, 0.5], None),

        # Tests with average aggregation
        ({"a": [1, 3], "b": [2, 4]}, ['a', 'b'], "average", [1.5, 3.5], None),
        ({"a": [1, 2, 3], "b": [4, 5, 6]}, ['a', 'b'], "average", [2.5, 3.5, 4.5], None),

        # Tests with standard deviation aggregation
        ({"a": [10, 10], "b": [20, 20]}, ['a', 'b'], "SD", [5.0, 5.0], None),
        ({"a": [10, 12, 23, 23], "b": [17, 15, 22, 20]}, ['a', 'b'], "SD", [3.5, 1.5, 0.5, 1.5], None),

        # Tests with inconsistent lengths
        ({"a": [1, 2, 3], "b": [3, 4]}, ['a', 'b'], "sum", None, ValueError),
    ])
def test_apply_horizontal_aggregation(report_data: Dict[str, List[float]],
                                      loop_list: List[str],
                                      aggregator_key: str,
                                      expected: List[float],
                                      expected_exception: Exception
                                      ) -> None:
    """
    Unit test for _apply_horizontal_aggregation() static method in report_generator.py file.
    """

    # Arrange
    aggregator = AGGREGATION_FUNCTIONS[aggregator_key]

    # Act and assert
    if expected_exception:
        with pytest.raises(expected_exception):
            ReportGenerator._apply_horizontal_aggregation(report_data, loop_list, aggregator)
    else:
        result = ReportGenerator._apply_horizontal_aggregation(report_data, loop_list, aggregator)
        assert result == expected


@pytest.mark.parametrize(
    "filtered_pool, filter_content, expected_result, expected_exception", [
        # Case with selected variables and slice parameters
        (
                {
                    "var1": {"values": [{"a": 1, "b": 2}, {"a": 3, "b": 4}]},
                    "var2": {"values": [{"a": 5, "b": 6}, {"a": 7, "b": 8}]}
                },
                {
                    "variables": ["a"],
                    "slice_start": 0,
                    "slice_end": 2
                },
                {"a": [1, 3, 5, 7], "name": "value"},
                None
        ),

        # Case without selected variables but required
        (
                {
                    "var1": {"values": [{"a": 1, "b": 2}, {"a": 3, "b": 4}]}
                },
                {},
                None,
                KeyError
        ),

        # Case with constants addition
        (
                {
                    "var1": {"values": [1, 2, 3, 4]}
                },
                {
                    "variables": ["var1"],
                    "constants": [{"name": "Constant1", "value": 10}]
                },
                {"name": "value", "var1": [1, 2, 3, 4]},
                None
        ),
    ]
)
def test_prepare_report_data_with_constants(filtered_pool: Dict[str, Dict[str, List[Any]]],
                                            filter_content: Dict[str, Any],
                                            expected_result: Dict[str, List[Any]],
                                            expected_exception: Exception,
                                            mocker: MockerFixture):
    """
    Unit test for the _prepare_report_data_with_constants method of ReportGenerator class in report_generator.py file.
    """

    # Arrange
    mocker.patch('RUFAS.report_generator.Utility.convert_list_of_dicts_to_dict_of_lists',
                 side_effect=lambda x: {k: [d[k] for d in x] for k in x[0]})
    mocker.patch.object(ReportGenerator, '_add_constants_data',
                        side_effect=lambda report_data, _: report_data.update({"name": "value"}))

    # Act and assert
    if expected_exception:
        with pytest.raises(expected_exception):
            ReportGenerator._prepare_report_data_with_constants(filtered_pool, filter_content)
    else:
        result = ReportGenerator._prepare_report_data_with_constants(filtered_pool, filter_content)
        assert result == expected_result


@pytest.mark.parametrize(
    "report_data, filter_content, expected_report_data, expected_exception", [
        # Case with constants added successfully
        (
                {"a": [1, 2, 3]},
                {
                    "constants": [
                        {"name": "Kilograms to Pounds", "value": 2.20462},
                        {"name": "Pounds to Dollars", "value": 10}
                    ]
                },
                {
                    "a": [1, 2, 3],
                    "Kilograms to Pounds": [2.20462, 2.20462, 2.20462],
                    "Pounds to Dollars": [10, 10, 10]
                },
                None
        ),

        # Case with report data containing lists of different lengths
        (
                {"a": [1, 2, 3], "b": [1, 2, 3, 4]},
                {
                    "constants": [
                        {"name": "Kilograms to Pounds", "value": 2.20462},
                        {"name": "Pounds to Dollars", "value": 10}
                    ]
                },
                {
                    "a": [1, 2, 3],
                    "b": [1, 2, 3, 4],
                    "Kilograms to Pounds": [2.20462, 2.20462, 2.20462, 2.20462],
                    "Pounds to Dollars": [10, 10, 10, 10]
                },
                None
        ),

        # Case where no constants are specified
        (
                {"a": [1, 2, 3]},
                {},
                {"a": [1, 2, 3]},
                None
        ),

        # Case with a constant name that already exists in report data
        (
                {"a": [1, 2, 3], "Kilograms to Pounds": [1, 1, 1]},
                {
                    "constants": [
                        {"name": "Kilograms to Pounds", "value": 2.20462}
                    ]
                },
                None,
                ValueError
        ),
    ]
)
def test_add_constants_data(report_data: Dict[str, List[Any]],
                            filter_content: Dict[str, Any],
                            expected_report_data: Dict[str, List[Any]],
                            expected_exception: Exception) -> None:
    """
    Unit test for the _add_constants_data method of ReportGenerator class in report_generator.py file.
    """

    # Act and assert
    if expected_exception:
        with pytest.raises(expected_exception):
            ReportGenerator._add_constants_data(report_data, filter_content)
    else:
        ReportGenerator._add_constants_data(report_data, filter_content)
        assert report_data == expected_report_data


@pytest.mark.parametrize(
    "filtered_pool, filter_content, mock_prep_data, expected_result, expected_exception", [
        # Case with valid horizontal and vertical aggregations
        (
                {"var1": {"values": [1, 2]}, "var2": {"values": [3, 4]}},
                {
                    "name": "Report",
                    "horizontal_aggregation": "sum",
                    "vertical_aggregation": "average",
                    "horizontal_order": ["var1", "var2"],
                    "horizontal_first": True
                },
                {"var1": [1, 2], "var2": [3, 4]},
                [6.0],
                None
        ),

        # Case with unsupported horizontal aggregation type
        (
                {"var1": {"values": [1, 2]}},
                {
                    "name": "Report",
                    "horizontal_aggregation": "unsupported"
                },
                {"var1": [1, 2]},
                None,
                ValueError
        ),

        # Case with no aggregation specified
        (
                {"var1": {"values": [1, 2]}},
                {"name": "Report"},
                {"var1": [1, 2]},
                None,
                ValueError
        ),

        # Case where report_data is empty after preparing with constants
        (
                {"var1": {"values": []}},
                {
                    "name": "Report",
                    "horizontal_aggregation": "sum"
                },
                {},
                None,
                ValueError
        ),

        # Case with only horizontal aggregation specified
        (
                {"var1": {"values": [1, 2]}, "var2": {"values": [3, 4]}},
                {
                    "name": "Report",
                    "horizontal_aggregation": "sum",
                    "horizontal_order": ["var1", "var2"]
                },
                {"var1": [1, 2], "var2": [3, 4]},
                [5, 7],
                None
        ),

        # Case with only vertical aggregation specified
        (
                {"var1": {"values": [1, 3]}, "var2": {"values": [2, 4]}},
                {
                    "name": "Report",
                    "vertical_aggregation": "average"
                },
                {"var1": [1, 3], "var2": [2, 4]},
                [3.5],
                None
        ),

        # Case with unsupported vertical aggregation type
        (
                {"var1": {"values": [1, 2]}},
                {
                    "name": "Report",
                    "vertical_aggregation": "unsupported"
                },
                {"var1": [1, 2]},
                None,
                ValueError
        ),

        # Case with unsupported horizontal aggregation type
        (
                {"var1": {"values": [1, 2]}},
                {
                    "name": "Report2",
                    "horizontal_aggregation": "unsupported"
                },
                {"var1": [1, 2]},
                None,
                ValueError
        ),

        # Case with only horizontal aggregation specified
        (
                {"var1": {"values": [1, 2]}, "var2": {"values": [3, 4]}},
                {
                    "name": "Report5",
                    "horizontal_aggregation": "sum",
                    "horizontal_order": ["var1", "var2"]
                },
                {"var1": [1, 2], "var2": [3, 4]},
                [5, 7],
                None
        ),

        # Use padding when lists have different lengths
        (
                {"var1": {"values": [1]}, "var2": {"values": [3, 4]}},
                {
                    "name": "Report",
                    "padding": {"method": "one"},
                    "horizontal_aggregation": "sum",
                },
                {"var1": [1], "var2": [3, 4]},
                [5, 7],
                None
        ),
    ]
)
def test_generate_aggregate_report(filtered_pool: Dict[str, Dict[str, List[Any]]],
                                   filter_content: Dict[str, Any],
                                   mock_prep_data: Dict[str, List[Any]],
                                   expected_result: List[Any],
                                   expected_exception: Exception,
                                   mocker: MockerFixture) -> None:
    """
    Unit test for the generate_aggregate_report() method of ReportGenerator class in report_generator.py file.
    """

    # Arrange
    mocker.patch.object(ReportGenerator, '_prepare_report_data_with_constants', return_value=mock_prep_data)
    patch_for_apply_padding = mocker.patch.object(ReportGenerator, '_apply_padding', return_value=None)
    mocker.patch.object(ReportGenerator, '_apply_horizontal_aggregation', return_value=[5, 7])
    mocker.patch.object(ReportGenerator, '_apply_vertical_aggregation', return_value=[3.5])

    # Act and assert
    if expected_exception:
        with pytest.raises(expected_exception):
            ReportGenerator.generate_aggregate_report(filtered_pool, filter_content)
    else:
        result = ReportGenerator.generate_aggregate_report(filtered_pool, filter_content)
        assert result == expected_result
        if filter_content.get("padding"):
            assert list(patch_for_apply_padding.call_args[0][0]) == list(mock_prep_data.values())
            assert patch_for_apply_padding.call_args[0][1] == filter_content["padding"]

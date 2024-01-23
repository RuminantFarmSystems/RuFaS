from __future__ import annotations
from typing import Dict, List, Any, Optional, Type
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
    report_generator = ReportGenerator()

    # Act
    result = report_generator._apply_vertical_aggregation(report_data, aggregator)

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
                                      expected_exception: Type[Exception]
                                      ) -> None:
    """
    Unit test for _apply_horizontal_aggregation() static method in report_generator.py file.
    """

    # Arrange
    aggregator = AGGREGATION_FUNCTIONS[aggregator_key]
    report_generator = ReportGenerator()

    # Act and assert
    if expected_exception:
        with pytest.raises(expected_exception):
            report_generator._apply_horizontal_aggregation(report_data, loop_list, aggregator)
    else:
        result = report_generator._apply_horizontal_aggregation(report_data, loop_list, aggregator)
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
                                            expected_exception: Type[Exception],
                                            mocker: MockerFixture):
    """
    Unit test for the _prepare_report_data_with_constants method of ReportGenerator class in report_generator.py file.
    """

    # Arrange
    report_generator = ReportGenerator()
    mocker.patch('RUFAS.report_generator.Utility.convert_list_of_dicts_to_dict_of_lists',
                 side_effect=lambda x: {k: [d[k] for d in x] for k in x[0]})
    mocker.patch.object(report_generator, '_add_constants_to_report_data',
                        side_effect=lambda report_data, _: report_data.update({"name": "value"}))

    # Act and assert
    if expected_exception:
        with pytest.raises(expected_exception):
            report_generator._prepare_report_data_with_constants(filtered_pool, filter_content)
    else:
        result = report_generator._prepare_report_data_with_constants(filtered_pool, filter_content)
        assert result == expected_result


@pytest.mark.parametrize(
    "report_data, filter_content, expected_report_data, expected_exception",
    [
        # Valid case with a valid constant
        (
                {"existing_data": [1, 2, 3]},
                {
                    "constants": {
                        "Constant1": 10
                    }
                },
                {
                    "existing_data": [1, 2, 3],
                    "Constant1": [10, 10, 10],
                },
                None),

        # Valid case with existing data of different lengths
        (
                {
                    "col1": [1, 2, 3],
                    "col2": [4, 5, 6, 7]
                },
                {
                    "constants": {
                        "Constant1": 10
                    }
                },
                {
                    "col1": [1, 2, 3],
                    "col2": [4, 5, 6, 7],
                    "Constant1": [10, 10, 10, 10]
                },
                None
        ),

        # Valid case with no constants
        (
                {"existing_data": [1, 2, 3]},
                {},
                {
                    "existing_data": [1, 2, 3]
                },
                None
        ),

        # Error case with a constant name that already exists in report_data
        (
                {
                    "Constant1": [5, 5, 5]
                },
                {
                    "constants": {
                        "Constant1": 10
                    }
                },
                None,
                ValueError
        ),
    ])
def test_add_constants_to_report_data(
        report_data: Dict[str, List[Any]],
        filter_content: Dict[str, Any],
        expected_report_data: Dict[str, List[Any]],
        expected_exception: Type[Exception]
) -> None:
    """
    Unit test for the _add_constants_to_report_data static method in report_generator.py file.
    """

    # Arrange
    report_generator = ReportGenerator()

    # Act and assert
    if expected_exception:
        with pytest.raises(expected_exception):
            report_generator._add_constants_to_report_data(report_data, filter_content)
    else:
        report_generator._add_constants_to_report_data(report_data, filter_content)
        assert report_data == expected_report_data


@pytest.mark.parametrize(
    "report_data, constant_config, expected_exception",
    [
        # Valid case with valid constants
        (
                {},
                {
                    "Constant1": 10,
                    "Constant2": 20.5
                },
                None
        ),

        # Error case with repeated constant name
        (
                {
                    "Constant1": [5, 5, 5]
                },
                {
                    "Constant1": 10
                },
                ValueError),

        # Error case with constant name None
        (
                {},
                {
                    None: 10
                },
                ValueError
        ),

        # Error case with constant value None
        (
                {},
                {
                    "Constant1": None
                },
                ValueError
        ),

        # Error case with constant name not a string
        (
                {},
                {
                    123: 10
                },
                ValueError
        ),

        # Error case with constant value not a number
        (
                {},
                {
                    "Constant1": "not_a_number"
                },
                ValueError
        ),

        # Error case with an empty constant name
        (
                {},
                {
                    "": 10
                },
                ValueError
        ),
    ])
def test_validate_constants(
        report_data: Dict[str, List[Any]],
        constant_config: Dict[str, Any],
        expected_exception: Type[Exception],
) -> None:
    """
    Unit test for the _validate_constants static method in report_generator.py file.
    """

    # Arrange
    report_generator = ReportGenerator()

    # Act and assert
    if expected_exception:
        with pytest.raises(expected_exception):
            report_generator._validate_constants(report_data, constant_config)
    else:
        report_generator._validate_constants(report_data, constant_config)


@pytest.mark.parametrize(
    "filtered_pool, filter_content, mock_prep_data,"
    "expected_result, expected_exception", [
        # Case with valid horizontal and vertical aggregations, with horizontal_first = True
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
                {'hor_ver_agg': [6.0]},
                None
        ),

        # Case with valid horizontal and vertical aggregations, with horizontal_first = False
        (
                {"var1": {"values": [1, 2]}, "var2": {"values": [3, 4]}},
                {
                    "name": "Report",
                    "horizontal_aggregation": "sum",
                    "vertical_aggregation": "average",
                    "horizontal_order": ["var1", "var2"],
                    "horizontal_first": False
                },
                {"var1": [1, 2], "var2": [3, 4]},
                {'ver_hor_agg': [3.5]},
                None
        ),

        # Case with no aggregation specified
        (
                {"var1": {"values": [1, 2]},
                 "var2": {"values": [3, 4]}},
                {"name": "Report"},
                {"var1": [1, 2],
                 "var2": [3, 4]},
                {"var1": [1, 2],
                 "var2": [3, 4]},
                None
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
                {'hor_agg': [5, 7]},
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
                {'ver_agg': [3.5]},
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
                {'hor_agg': [5, 7]},
                None
        ),
    ]
)
def test_perform_aggregations(
        filtered_pool: Dict[str, Dict[str, List[Any]]],
        filter_content: Dict[str, Any],
        mock_prep_data: Dict[str, List[Any]],
        expected_result: List[Any],
        expected_exception: Type[Exception],
        mocker: MockerFixture) -> None:
    """
    Unit test for the _perform_aggregations() method of ReportGenerator class in report_generator.py file.
    """

    # Arrange
    report_generator = ReportGenerator()
    mocker.patch.object(report_generator, '_prepare_report_data_with_constants', return_value=mock_prep_data)
    mocker.patch.object(report_generator, '_apply_horizontal_aggregation', return_value=[5, 7])
    mocker.patch.object(report_generator, '_apply_vertical_aggregation', return_value=[3.5])

    # Act and assert
    if expected_exception:
        with pytest.raises(expected_exception):
            report_generator._perform_aggregations(filtered_pool, filter_content)
    else:
        result = report_generator._perform_aggregations(filtered_pool, filter_content)
        assert result == expected_result


@pytest.mark.parametrize(
    "filter_content, expected_horizontal, expected_vertical, expected_exception",
    [
        # Test with valid horizontal and vertical keys
        ({"horizontal_aggregation": "sum", "vertical_aggregation": "average"}, "sum", "average", None),

        # Test with valid horizontal key and no vertical key
        ({"horizontal_aggregation": "product"}, "product", None, None),

        # Test with no horizontal key and valid vertical key
        ({"vertical_aggregation": "division"}, None, "division", None),

        # Test with unsupported horizontal key
        ({"horizontal_aggregation": "unsupported_key", "vertical_aggregation": "sum"}, None, None, ValueError),

        # Test with unsupported vertical key
        ({"horizontal_aggregation": "sum", "vertical_aggregation": "unsupported_key"}, None, None, ValueError),

        # Test with both keys unsupported
        ({"horizontal_aggregation": "unsupported_h", "vertical_aggregation": "unsupported_v"}, None, None, ValueError),

        # Test with empty filter content
        ({}, None, None, None),
    ]
)
def test_extract_and_check_aggregation_keys(
        filter_content: Dict[str, Any],
        expected_horizontal: str | None,
        expected_vertical: str | None,
        expected_exception: Type[Exception]
):
    """
    Unit test for _extract_and_check_aggregation_keys() method in report_generator.py file.
    """
    # Arrange
    report_generator = ReportGenerator()

    # Act and assert
    if expected_exception:
        with pytest.raises(expected_exception):
            report_generator._extract_and_check_aggregation_keys(filter_content)
    else:
        horizontal_key, vertical_key = report_generator._extract_and_check_aggregation_keys(filter_content)
        assert horizontal_key == expected_horizontal
        assert vertical_key == expected_vertical


@pytest.mark.parametrize(
    "horizontally_aggregated, vertically_aggregated, filter_content, expected",
    [
        # Test case with both horizontal and vertical aggregation, horizontal first
        ([1, 2, 3], [4, 5, 6],
         {"horizontal_aggregation": "sum", "vertical_aggregation": "sum", "horizontal_first": True},
         {"hor_ver_agg": [sum([1, 2, 3])]}),

        # Test case with both horizontal and vertical aggregation, vertical first
        ([1, 2, 3], [4, 5, 6],
         {"horizontal_aggregation": "sum", "vertical_aggregation": "sum", "horizontal_first": False},
         {"ver_hor_agg": [sum([4, 5, 6])]}),

        # Test case with only horizontal aggregation
        ([1, 2, 3], None,
         {"horizontal_aggregation": "sum"},
         {"hor_agg": [1, 2, 3]}),

        # Test case with only vertical aggregation
        (None, [4, 5, 6],
         {"vertical_aggregation": "sum"},
         {"ver_agg": [4, 5, 6]}),

        # Test case with no aggregation
        (None, None, {}, None),
    ]
)
def test_combine_aggregate_report_data(
        horizontally_aggregated: List[int | float] | None,
        vertically_aggregated: List[int | float] | None,
        filter_content: Dict[str, Any],
        expected: Dict[str, List[int | float]] | None
) -> None:
    """
    Unit test for _combine_aggregate_report_data() method in report_generator.py file.
    """
    # Arrange
    report_generator = ReportGenerator()

    # Act
    result = report_generator._combine_aggregate_report_data(horizontally_aggregated, vertically_aggregated,
                                                             filter_content)
    # Assert
    assert result == expected


@pytest.mark.parametrize(
    "references, reports, expected_exception, expected_message",
    [
        # All references are present
        (["ref1", "ref2"], {"ref1": {}, "ref2": {}}, None, None),

        # One reference is missing
        (["ref1", "ref2"], {"ref1": {}}, KeyError, "Missing referenced reports: ref2"),

        # Multiple references are missing
        (["ref1", "ref2", "ref3"], {"ref1": {}}, KeyError, "Missing referenced reports: ref2, ref3"),

        # Reports dictionary is empty
        (["ref1"], {}, KeyError, "Missing referenced reports: ref1"),
    ]
)
def test_check_for_missing_references(mocker: MockerFixture,
                                      references: List[str],
                                      reports: Dict[str, Dict[str, Any]],
                                      expected_exception: Optional[Exception],
                                      expected_message: Optional[str]) -> None:
    """
    Unit test for _check_for_missing_references static method in report_generator.py file.
    """

    # Arrange
    mocker.patch('RUFAS.report_generator.ReportGenerator.__init__', return_value=None)
    report_generator = ReportGenerator()
    report_generator.reports = reports

    if expected_exception:
        # Act and assert
        with pytest.raises(expected_exception) as excinfo:  # type: ignore
            report_generator._check_for_missing_references(references)
        assert expected_message in str(excinfo.value)
    else:
        # Act
        report_generator._check_for_missing_references(references)


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
    ]
)
def test_ensure_unique_report_name_with_timestamp(
        mocker: MockerFixture,
        report_name: str,
        reports: Dict[str, Dict[str, Any]],
        expected_name: str,
        timestamp_return_value: str
):
    """
    Unit test for _ensure_unique_report_name_with_timestamp method in report_generator.py file.
    """

    # Arrange
    mocker.patch('RUFAS.report_generator.ReportGenerator.__init__', return_value=None)
    report_generator = ReportGenerator()
    report_generator.reports = reports
    mocker.patch('RUFAS.util.Utility.get_timestamp', return_value=timestamp_return_value)

    # Act
    result = report_generator._ensure_unique_report_name_with_timestamp(report_name)

    # Assert
    assert result == expected_name


@pytest.mark.parametrize(
    "filter_content, filtered_pool, reports, reference_exception, "
    "perform_aggregations_exception, expected_report_columns, expected_log_messages",
    [
        # Standard report generation
        (
                {"name": "standard_report", "filters": ["some_filter"]},
                {"some_filter": [1, 2, 3]},
                {},
                None,
                None,
                {"standard_report_some_filter": {"values": [1, 2, 3]}},
                ["Start generating individual report: standard_report"]
        ),

        # Report with name as an empty string
        (
                {"name": "", "filters": ["some_filter"]},
                {"some_filter": [1, 2, 3]},
                {},
                None,
                None,
                {"some_filter": {"values": [1, 2, 3]}},
                ["Start generating individual report: "]
        ),

        # Report with cross-references
        (
                {
                    "name": "report_with_references",
                    "filters": ["some_filter"],
                    "cross_references": ["ref1"]
                },
                {"some_filter": [1, 2, 3]},
                {"ref1": {"values": [4, 5, 6]}},
                None,
                None,
                {
                    "ref1": {"values": [4, 5, 6]},
                    "report_with_references_some_filter": {"values": [1, 2, 3]},
                    "report_with_references_ref1": {"values": [4, 5, 6]}},
                ["Start generating individual report: report_with_references"]
        ),

        # Report generation with missing cross-references
        (
                {"name": "error_report", "cross_references": ["missing_ref"]},
                {},
                {"ref": {"values": [1, 2, 3]}},
                KeyError,
                None,
                None,
                ["Start generating individual report: error_report",
                 "Error generating the individual report (error_report) => KeyError: "]
        ),

        # Report generation with error in _perform_aggregations
        (
                {"name": "error_report", "filters": ["some_filter"]},
                {"some_data_key": [1, 2, 3]},
                {},
                None,
                ValueError,
                None,
                ["Start generating individual report: error_report",
                 "Error generating the individual report (error_report) => ValueError: "]
        ),
    ]
)
def test_generate_report(
        filter_content: Dict[str, Any],
        filtered_pool: Dict[str, Any],
        reports: Dict[str, Dict[str, List[Any]]],
        reference_exception: Optional[Type[BaseException]],
        perform_aggregations_exception: Optional[Type[BaseException]],
        expected_report_columns: Dict[str, List[Any]],
        expected_log_messages: List[str],
        mocker: MockerFixture,
) -> None:
    """
    Unit test for the generate_report method in the ReportGenerator class.
    """

    # Arrange
    mocker.patch('RUFAS.report_generator.ReportGenerator.__init__', return_value=None)
    report_generator = ReportGenerator()
    report_generator.reports = reports
    mocker.patch.object(report_generator, '_ensure_unique_report_name_with_timestamp',
                        side_effect=lambda name: name)
    mocker.patch.object(report_generator, '_check_for_missing_references',
                        side_effect=reference_exception if reference_exception else None)
    if perform_aggregations_exception:
        mocker.patch.object(report_generator, '_perform_aggregations',
                            side_effect=perform_aggregations_exception)
    elif not reference_exception:
        mocker.patch.object(report_generator, '_perform_aggregations',
                            return_value={fltr: filtered_pool[fltr] for fltr in filter_content["filters"]} |
                                         {ref: reports[ref]["values"]
                                          for ref in filter_content.get("cross_references", [])})

    # Act
    event_logs = report_generator.generate_report(filter_content, filtered_pool)

    # Assert
    if not reference_exception and not perform_aggregations_exception:
        assert report_generator.reports == expected_report_columns

    log_messages = [log["message"] for log in event_logs]
    for expected_message in expected_log_messages:
        assert expected_message in log_messages


def test_report_generator_init() -> None:
    """
    Unit test for the __init__ method of ReportGenerator class in report_generator.py file.
    """

    # Arrange
    expected_reports = {}

    # Act
    report_generator = ReportGenerator()

    # Assert
    assert report_generator.reports == expected_reports


def test_clear_reports() -> None:
    """
    Unit test for the clear_reports method of ReportGenerator class in report_generator.py file.
    """

    # Arrange
    report_generator = ReportGenerator()
    report_generator.reports = {"report1": {}, "report2": {}}

    # Act
    report_generator.clear_reports()

    # Assert
    assert report_generator.reports == {}

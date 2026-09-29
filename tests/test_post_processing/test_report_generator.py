import logging
from typing import Any, Callable

import numpy as np
import pytest
from pytest_mock import MockerFixture

from RUFAS.post_processing.report_generator import AGGREGATION_FUNCTIONS, ReportGenerator, ReportGeneratorConfig
from RUFAS.post_processing.unit_handler import UnitHandler
from RUFAS.util import Aggregator


@pytest.fixture
def report_generator() -> ReportGenerator:
    return ReportGenerator(ReportGeneratorConfig(metadata_prefix="test_prefix"))


def test_aggregation_functions() -> None:
    """Unit test for the aggregation functions supported by ReportGenerator."""
    assert AGGREGATION_FUNCTIONS == {
        "average": Aggregator.average,
        "division": Aggregator.division,
        "product": Aggregator.product,
        "SD": Aggregator.standard_deviation,
        "sum": Aggregator.sum,
        "subtraction": Aggregator.subtraction,
    }


def test_report_generator_config_defaults() -> None:
    """Unit test for the default values of ReportGeneratorConfig."""
    config = ReportGeneratorConfig()

    assert config.metadata_prefix == ""
    assert config.time is None


def test_report_generator_init(mocker: MockerFixture) -> None:
    """Unit test for the __init__ method of ReportGenerator."""
    mock_time = mocker.MagicMock()

    report_generator = ReportGenerator(ReportGeneratorConfig(metadata_prefix="test_prefix", time=mock_time))

    assert report_generator.reports == {}
    assert report_generator.metadata_prefix == "test_prefix"
    assert report_generator.time == mock_time
    assert isinstance(report_generator.unit_handler, UnitHandler)
    assert report_generator.unit_handler.metadata_prefix == "test_prefix"
    assert report_generator._logger.name == "RUFAS.ReportGenerator"


@pytest.mark.parametrize("level", [logging.INFO, logging.WARNING, logging.ERROR])
def test_log(level: int, report_generator: ReportGenerator, mocker: MockerFixture) -> None:
    """Unit test for the _log method of ReportGenerator."""
    mock_logger_log = mocker.patch.object(report_generator._logger, "log")

    report_generator._log(level, "log_name", "log message", "function_name")

    mock_logger_log.assert_called_once_with(
        level,
        "log message",
        extra={
            "rufas_name": "log_name",
            "rufas_info_map": {
                "class": "ReportGenerator",
                "function": "function_name",
                "metadata_prefix": "test_prefix",
            },
        },
    )


def test_clear_reports(report_generator: ReportGenerator) -> None:
    """Unit test for the clear_reports method of ReportGenerator."""
    report_generator.reports = {"report1": {}, "report2": {}}

    report_generator.clear_reports()

    assert report_generator.reports == {}


@pytest.mark.parametrize(
    "filter_contents, filtered_pools, expected_reports",
    [
        # Report with a single column
        (
            [{"name": "standard_report", "filters": ["some_filter"]}],
            [{"some_filter": {"values": [1, 2, 3]}}],
            {"standard_report": {"values": [1, 2, 3]}},
        ),
        # Report with a single column and a verbose name
        (
            [{"name": "standard_report", "filters": ["some_filter"], "use_verbose_report_name": True}],
            [{"some_filter": {"values": [1, 2, 3]}}],
            {"standard_report_some_filter": {"values": [1, 2, 3]}},
        ),
        # Report with multiple columns
        (
            [{"name": "standard_report", "filters": ["some_filter", "other_filter"]}],
            [{"some_filter": {"values": [1, 2, 3]}, "other_filter": {"values": ["a", "b"]}}],
            {
                "standard_report_some_filter": {"values": [1, 2, 3]},
                "standard_report_other_filter": {"values": ["a", "b"]},
            },
        ),
        # Report with an empty name
        (
            [{"name": "", "filters": ["some_filter"]}],
            [{"some_filter": {"values": [1, 2, 3]}}],
            {"some_filter": {"values": [1, 2, 3]}},
        ),
        # Report with rounded data
        (
            [{"name": "test_report", "filters": ["filter1"], "data_significant_digits": 2}],
            [{"filter1": {"values": [1.23456789, 2.3456789, 3.456789]}}],
            {"test_report": {"values": [1.23, 2.35, 3.46]}},
        ),
        # Report with units
        (
            [{"name": "Milk", "filters": ["milk"], "display_units": True}],
            [{"milk": {"values": [10.0, 20.0], "info_maps": [{"units": "kg"}]}}],
            {"Milk": {"values": [10.0, 20.0]}},
        ),
        # Reports with aggregations and cross-references
        (
            [
                {"name": "Milk", "filters": ["milk"], "vertical_aggregation": "sum"},
                {"name": "Cows", "filters": ["cows"], "vertical_aggregation": "average"},
                {
                    "name": "Milk per cow",
                    "cross_references": ["Milk_ver_agg", "Cows_ver_agg"],
                    "horizontal_aggregation": "division",
                },
            ],
            [{"milk": {"values": [10.0, 20.0]}}, {"cows": {"values": [2, 4]}}, {}],
            {
                "Milk_ver_agg": {"values": [30.0]},
                "Cows_ver_agg": {"values": [3.0]},
                "Milk per cow_hor_agg": {"values": [10.0]},
            },
        ),
        # Reports with aggregations, cross-references, and units
        (
            [
                {"name": "Milk", "filters": ["milk"], "vertical_aggregation": "sum", "display_units": True},
                {"name": "Cows", "filters": ["cows"], "vertical_aggregation": "average", "display_units": True},
                {
                    "name": "Milk per cow",
                    "cross_references": ["Milk_ver_agg_.*", "Cows_ver_agg_.*"],
                    "horizontal_aggregation": "division",
                    "display_units": True,
                },
            ],
            [
                {"milk": {"values": [10.0, 20.0], "info_maps": [{"units": "kg"}]}},
                {"cows": {"values": [2, 4], "info_maps": [{"units": "animal"}]}},
                {},
            ],
            {
                "Milk_ver_agg_(kg)": {"values": [30.0]},
                "Cows_ver_agg_(animal)": {"values": [3.0]},
                "Milk per cow_hor_agg_(kg/animal)": {"values": [10.0]},
            },
        ),
        # Reports with constants
        (
            [
                {
                    "name": "Gallons",
                    "filters": ["milk"],
                    "constants": {"Liters to Gallons": 0.25},
                    "horizontal_aggregation": "product",
                },
                {
                    "name": "Grams",
                    "filters": ["milk"],
                    "constants": {"KG_TO_GRAMS": 1000},
                    "horizontal_aggregation": "product",
                    "display_units": True,
                },
            ],
            [
                {"milk": {"values": [10.0, 20.0]}},
                {"milk": {"values": [10.0, 20.0], "info_maps": [{"units": "kg"}]}},
            ],
            {"Gallons_hor_agg": {"values": [2.5, 5.0]}, "Grams_hor_agg_(g)": {"values": [10000.0, 20000.0]}},
        ),
        # Report with both aggregations
        (
            [
                {
                    "name": "Heifers",
                    "filters": ["heifers"],
                    "vertical_aggregation": "sum",
                    "horizontal_aggregation": "sum",
                    "horizontal_first": True,
                }
            ],
            [{"heiferIs": {"values": [1, 2, 3]}, "heiferIIs": {"values": [4, 5, 6]}}],
            {"Heifers_hor_ver_agg": {"values": [21]}},
        ),
    ],
)
def test_generate_report(
    filter_contents: list[dict[str, Any]],
    filtered_pools: list[dict[str, dict[str, list[Any]]]],
    expected_reports: dict[str, dict[str, list[Any]]],
    report_generator: ReportGenerator,
    mocker: MockerFixture,
) -> None:
    """Unit test for the generate_report method of ReportGenerator."""
    mock_log = mocker.patch.object(report_generator, "_log")
    mocker.patch.object(report_generator.unit_handler, "_log")

    for filter_content, filtered_pool in zip(filter_contents, filtered_pools):
        report_generator.generate_report(filter_content, filtered_pool)

    assert report_generator.reports == expected_reports
    start_logs = [call for call in mock_log.call_args_list if call.args[1] == "start_generate_individual_report"]
    assert start_logs == [
        mocker.call(
            logging.INFO,
            "start_generate_individual_report",
            f"Start generating individual report: {filter_content['name']}",
            "generate_report",
        )
        for filter_content in filter_contents
    ]
    assert all(call.args[0] != logging.ERROR for call in mock_log.call_args_list)


def test_generate_report_with_untitled_report(report_generator: ReportGenerator, mocker: MockerFixture) -> None:
    """Unit test for the generate_report method of ReportGenerator when the report has no name."""
    mock_log = mocker.patch.object(report_generator, "_log")
    mocker.patch("RUFAS.post_processing.report_generator.Utility.get_timestamp", return_value="2023-01-01")

    report_generator.generate_report({"filters": ["some_filter"]}, {"some_filter": {"values": [1, 2, 3]}})

    assert report_generator.reports == {"untitled_2023-01-01": {"values": [1, 2, 3]}}
    mock_log.assert_called_once_with(
        logging.INFO,
        "start_generate_individual_report",
        "Start generating individual report: untitled_2023-01-01",
        "generate_report",
    )


def test_generate_report_calls(report_generator: ReportGenerator, mocker: MockerFixture) -> None:
    """Unit test for the functions called by the generate_report method of ReportGenerator."""
    filter_content = {"name": "report", "filters": ["some_filter"], "data_significant_digits": 1}
    filtered_pool = {"some_filter": {"values": [1.23]}}
    report_pool = {"reference": {"values": [4.56]}, "some_filter": {"values": [1.23]}}
    report_data = {"hor_agg": [5.79]}
    rounded_report_data = {"hor_agg": [5.8]}
    report_filter_data = {"report_hor_agg": {"values": [5.8]}}
    mocker.patch.object(report_generator, "_log")
    mock_ensure_unique_name = mocker.patch.object(
        report_generator, "_ensure_unique_report_name_with_timestamp", return_value="unique_report"
    )
    mock_add_cross_references = mocker.patch.object(
        report_generator, "_add_cross_references_to_pool", return_value=report_pool
    )
    mock_perform_aggregations = mocker.patch.object(
        report_generator, "_perform_aggregations", return_value=(report_data, True)
    )
    mock_round = mocker.patch(
        "RUFAS.post_processing.report_generator.Utility.round_numeric_values_in_dict",
        return_value=rounded_report_data,
    )
    mock_name_report_columns = mocker.patch.object(
        report_generator, "_name_report_columns", return_value=report_filter_data
    )
    mock_store_or_graph = mocker.patch.object(report_generator, "_store_or_graph_report_data")

    report_generator.generate_report(filter_content, filtered_pool)

    mock_ensure_unique_name.assert_called_once_with("report")
    mock_add_cross_references.assert_called_once_with(filter_content, filtered_pool)
    mock_perform_aggregations.assert_called_once_with(report_pool, filter_content)
    mock_round.assert_called_once_with(report_data, 1)
    mock_name_report_columns.assert_called_once_with(rounded_report_data, filter_content, "unique_report", True)
    mock_store_or_graph.assert_called_once_with(report_filter_data, filter_content, "unique_report")


def test_generate_report_without_rounding(report_generator: ReportGenerator, mocker: MockerFixture) -> None:
    """Unit test for the generate_report method of ReportGenerator when the data is not rounded."""
    mocker.patch.object(report_generator, "_log")
    mock_round = mocker.patch("RUFAS.post_processing.report_generator.Utility.round_numeric_values_in_dict")

    report_generator.generate_report(
        {"name": "report", "filters": ["some_filter"]}, {"some_filter": {"values": [1.23]}}
    )

    mock_round.assert_not_called()
    assert report_generator.reports == {"report": {"values": [1.23]}}


@pytest.mark.parametrize(
    "filter_content, filtered_pool, expected_error_message",
    [
        # Missing cross-references
        (
            {"name": "error_report", "cross_references": ["missing_ref"]},
            {},
            "Error generating report (error_report) => KeyError: 'Report Generator error: Missing referenced "
            "reports matching the following pattern(s): missing_ref'",
        ),
        # Unsupported aggregation function
        (
            {"name": "error_report", "filters": ["some_filter"], "vertical_aggregation": "median"},
            {"some_filter": {"values": [1, 2, 3]}},
            "Error generating report (error_report) => KeyError: 'median'",
        ),
        # Empty column
        (
            {"name": "error_report", "filters": ["some_filter"]},
            {"some_filter": {"values": []}},
            "Error generating report (error_report) => ValueError: Report Generator error: One or more columns in "
            "the report data are empty, cannot perform aggregations.",
        ),
        # No data
        (
            {"name": "error_report", "filters": ["some_filter"]},
            {},
            "Error generating report (error_report) => ValueError: Report Generator error: filter ['some_filter'] "
            "in error_report led to empty report data.",
        ),
        # Invalid constant
        (
            {"name": "error_report", "filters": ["some_filter"], "constants": {"constant": "ten"}},
            {"some_filter": {"values": [1, 2, 3]}},
            "Error generating report (error_report) => ValueError: Report Generator error: Constant value ten must "
            "be a number.",
        ),
        # Data with different lengths aggregated horizontally
        (
            {"name": "error_report", "filters": ["some_filter"], "horizontal_aggregation": "sum"},
            {"some_filter": {"values": [1, 2, 3]}, "other_filter": {"values": [1, 2]}},
            "Error generating report (error_report) => ValueError: Report Generator error: Can't aggregate data "
            "with different lengths",
        ),
    ],
)
def test_generate_report_with_error(
    filter_content: dict[str, Any],
    filtered_pool: dict[str, dict[str, list[Any]]],
    expected_error_message: str,
    report_generator: ReportGenerator,
    mocker: MockerFixture,
) -> None:
    """Unit test for the generate_report method of ReportGenerator when the report cannot be generated."""
    report_generator.reports = {"existing_report": {"values": [1, 2, 3]}}
    mock_log = mocker.patch.object(report_generator, "_log")

    report_generator.generate_report(filter_content, filtered_pool)

    assert report_generator.reports == {"existing_report": {"values": [1, 2, 3]}}
    assert mock_log.call_args_list == [
        mocker.call(
            logging.INFO,
            "start_generate_individual_report",
            "Start generating individual report: error_report",
            "generate_report",
        ),
        mocker.call(logging.ERROR, "report_generation_error", expected_error_message, "generate_report"),
    ]


def test_generate_report_with_unexpected_error(report_generator: ReportGenerator, mocker: MockerFixture) -> None:
    """Unit test for the generate_report method of ReportGenerator when an unexpected error is raised."""
    mocker.patch.object(report_generator, "_log")
    mocker.patch.object(report_generator, "_perform_aggregations", side_effect=TypeError("unexpected"))

    with pytest.raises(TypeError, match="unexpected"):
        report_generator.generate_report({"name": "report", "filters": ["a"]}, {"a": {"values": [1]}})


def test_add_cross_references_to_pool_without_cross_references(
    report_generator: ReportGenerator, mocker: MockerFixture
) -> None:
    """Unit test for the _add_cross_references_to_pool method of ReportGenerator without cross-references."""
    filtered_pool = {"some_filter": {"values": [1, 2, 3]}}
    report_generator.reports = {"ref1": {"values": [4, 5, 6]}}
    mock_check_for_missing_references = mocker.patch.object(report_generator, "_check_for_missing_references")
    mock_get_reports_by_regex = mocker.patch.object(report_generator, "_get_reports_by_regex")

    result = report_generator._add_cross_references_to_pool({"name": "report"}, filtered_pool)

    assert result is filtered_pool
    mock_check_for_missing_references.assert_not_called()
    mock_get_reports_by_regex.assert_not_called()


@pytest.mark.parametrize(
    "cross_references, filtered_pool, expected",
    [
        # Cross-references only
        (["ref1"], {}, {"ref1": {"values": [4, 5, 6]}}),
        # Cross-references come before the data in the filtered pool
        (
            ["ref\\d"],
            {"some_filter": {"values": [1, 2, 3]}},
            {"ref1": {"values": [4, 5, 6]}, "ref2": {"values": [7, 8, 9]}, "some_filter": {"values": [1, 2, 3]}},
        ),
        # Data in the filtered pool replaces the cross-referenced report with the same name
        (["ref1"], {"ref1": {"values": [1, 2, 3]}}, {"ref1": {"values": [1, 2, 3]}}),
    ],
)
def test_add_cross_references_to_pool(
    cross_references: list[str],
    filtered_pool: dict[str, dict[str, list[Any]]],
    expected: dict[str, dict[str, list[Any]]],
    report_generator: ReportGenerator,
) -> None:
    """Unit test for the _add_cross_references_to_pool method of ReportGenerator."""
    reports = {"ref1": {"values": [4, 5, 6]}, "ref2": {"values": [7, 8, 9]}, "report": {"values": [0]}}
    report_generator.reports = dict(reports)

    result = report_generator._add_cross_references_to_pool({"cross_references": cross_references}, filtered_pool)

    assert list(result.items()) == list(expected.items())
    assert report_generator.reports == reports


def test_add_cross_references_to_pool_missing_references(report_generator: ReportGenerator) -> None:
    """Unit test for the _add_cross_references_to_pool method of ReportGenerator with missing cross-references."""
    report_generator.reports = {"ref1": {"values": [4, 5, 6]}}

    with pytest.raises(KeyError, match="Missing referenced reports matching the following pattern"):
        report_generator._add_cross_references_to_pool({"cross_references": ["ref1", "ref2"]}, {})


@pytest.mark.parametrize(
    "report_data, filter_content, individual_report_name, is_report_aggregated, expected",
    [
        # Single column that is not aggregated
        ({"col": [1, 2]}, {}, "report", False, {"report": {"values": [1, 2]}}),
        ({"col": [1, 2]}, {"use_verbose_report_name": False}, "report", False, {"report": {"values": [1, 2]}}),
        # Single column that is not aggregated, with a verbose name
        ({"col": [1, 2]}, {"use_verbose_report_name": True}, "report", False, {"report_col": {"values": [1, 2]}}),
        # Single column that is aggregated
        ({"ver_agg": [3]}, {}, "report", True, {"report_ver_agg": {"values": [3]}}),
        ({"ver_agg": [3]}, {"use_verbose_report_name": True}, "report", True, {"report_ver_agg": {"values": [3]}}),
        # Multiple columns
        (
            {"col1": [1, 2], "col2": [3, 4]},
            {},
            "report",
            False,
            {"report_col1": {"values": [1, 2]}, "report_col2": {"values": [3, 4]}},
        ),
        (
            {"col1_ver_agg": [3], "col2_ver_agg": [7]},
            {},
            "report",
            True,
            {"report_col1_ver_agg": {"values": [3]}, "report_col2_ver_agg": {"values": [7]}},
        ),
        # Empty report name
        ({"col": [1, 2]}, {}, "", False, {"col": {"values": [1, 2]}}),
        ({"col": [1, 2]}, {"use_verbose_report_name": True}, "", False, {"col": {"values": [1, 2]}}),
        ({"col1": [1, 2], "col2": [3, 4]}, {}, "", True, {"col1": {"values": [1, 2]}, "col2": {"values": [3, 4]}}),
        # Names already used by previously generated reports
        ({"col": [1, 2]}, {}, "existing_report", False, {"existing_report_2023-01-01": {"values": [1, 2]}}),
        (
            {"col1": [1, 2], "col2": [3, 4]},
            {},
            "existing",
            False,
            {"existing_col1_2023-01-01": {"values": [1, 2]}, "existing_col2": {"values": [3, 4]}},
        ),
        # No columns
        ({}, {}, "report", False, {}),
    ],
)
def test_name_report_columns(
    report_data: dict[str, list[Any]],
    filter_content: dict[str, Any],
    individual_report_name: str,
    is_report_aggregated: bool,
    expected: dict[str, dict[str, list[Any]]],
    report_generator: ReportGenerator,
    mocker: MockerFixture,
) -> None:
    """Unit test for the _name_report_columns method of ReportGenerator."""
    report_generator.reports = {"existing_report": {"values": [0]}, "existing_col1": {"values": [0]}}
    mocker.patch("RUFAS.post_processing.report_generator.Utility.get_timestamp", return_value="2023-01-01")

    result = report_generator._name_report_columns(
        report_data, filter_content, individual_report_name, is_report_aggregated
    )

    assert result == expected


@pytest.mark.parametrize(
    "filter_content, expected_reports, is_graphed, is_warning_logged",
    [
        # Report data is only stored
        ({"name": "report"}, {"existing": {"values": [0]}, "report": {"values": [1, 2]}}, False, False),
        ({"graph_and_report": False}, {"existing": {"values": [0]}, "report": {"values": [1, 2]}}, False, False),
        # Report data is only graphed
        ({"graph_details": {"type": "plot"}}, {"existing": {"values": [0]}}, True, False),
        (
            {"graph_details": {"type": "plot"}, "graph_and_report": False},
            {"existing": {"values": [0]}},
            True,
            False,
        ),
        # Report data is stored and graphed
        (
            {"graph_details": {"type": "plot"}, "graph_and_report": True},
            {"existing": {"values": [0]}, "report": {"values": [1, 2]}},
            True,
            False,
        ),
        # Report data is requested to be stored and graphed without the graph details
        ({"graph_and_report": True}, {"existing": {"values": [0]}, "report": {"values": [1, 2]}}, False, True),
        (
            {"graph_details": {}, "graph_and_report": True},
            {"existing": {"values": [0]}, "report": {"values": [1, 2]}},
            False,
            True,
        ),
    ],
)
def test_store_or_graph_report_data(
    filter_content: dict[str, Any],
    expected_reports: dict[str, dict[str, list[Any]]],
    is_graphed: bool,
    is_warning_logged: bool,
    report_generator: ReportGenerator,
    mocker: MockerFixture,
) -> None:
    """Unit test for the _store_or_graph_report_data method of ReportGenerator."""
    report_generator.reports = {"existing": {"values": [0]}}
    report_filter_data = {"report": {"values": [1, 2]}}
    mock_log = mocker.patch.object(report_generator, "_log")
    mock_prepare_report_data_to_be_graphed = mocker.patch.object(report_generator, "_prepare_report_data_to_be_graphed")

    report_generator._store_or_graph_report_data(report_filter_data, filter_content, "report")

    assert report_generator.reports == expected_reports
    if is_graphed:
        mock_prepare_report_data_to_be_graphed.assert_called_once_with(report_filter_data, filter_content, "report")
    else:
        mock_prepare_report_data_to_be_graphed.assert_not_called()
    if is_warning_logged:
        mock_log.assert_called_once_with(
            logging.WARNING,
            "report_generation_warning",
            "Request to graph and report data not fulfilled - no graph_details present in report filter file.",
            "_store_or_graph_report_data",
        )
    else:
        mock_log.assert_not_called()


@pytest.mark.parametrize(
    "filter_content, expected_result",
    [
        ({"horizontal_first": True}, True),
        ({"horizontal_first": False}, False),
        ({}, False),
        ({"horizontal_first": None}, False),
    ],
)
def test_get_horizontal_first_value(
    filter_content: dict[str, Any], expected_result: bool, report_generator: ReportGenerator
) -> None:
    """Unit test for the _get_horizontal_first_value method of ReportGenerator."""
    assert report_generator._get_horizontal_first_value(filter_content) == expected_result


def test_prepare_report_data_to_be_graphed(mocker: MockerFixture) -> None:
    """Unit test for the _prepare_report_data_to_be_graphed method of ReportGenerator."""
    mock_time = mocker.MagicMock()
    report_generator = ReportGenerator(ReportGeneratorConfig(metadata_prefix="test_prefix", time=mock_time))
    graph_data = {"test_report": {"values": [1, 2, 3]}}
    graph_details = {
        "metadata_prefix": "prefix",
        "graphics_dir": "dir",
        "type": "plot",
        "title": "graph title",
        "produce_graphics": False,
    }
    filter_content = {"name": "example_report", "filters": ["filter1", "filter2"], "graph_details": dict(graph_details)}
    graph_event_log = [{"log": "log name", "message": "Graph generated", "info_map": {"class": "GraphGenerator"}}]
    mock_graph_generator = mocker.patch("RUFAS.post_processing.report_generator.GraphGenerator")
    mock_graph_generator.return_value.generate_graph.return_value = graph_event_log
    mock_log_graph_generator_events = mocker.patch.object(report_generator, "_log_graph_generator_events")

    report_generator._prepare_report_data_to_be_graphed(graph_data, filter_content, "test_report")

    mock_graph_generator.assert_called_once_with("prefix", time=mock_time)
    mock_graph_generator.return_value.generate_graph.assert_called_once_with(
        graph_data,
        {
            "metadata_prefix": "prefix",
            "type": "plot",
            "title": "example_report",
            "produce_graphics": False,
            "filters": ["filter1", "filter2"],
            "is_aggregated_report_data": True,
        },
        "test_report",
        "dir",
        False,
    )
    mock_log_graph_generator_events.assert_called_once_with(graph_event_log)
    assert filter_content["graph_details"] == graph_details


def test_prepare_report_data_to_be_graphed_defaults(report_generator: ReportGenerator, mocker: MockerFixture) -> None:
    """Unit test for the default values used by the _prepare_report_data_to_be_graphed method of ReportGenerator."""
    graph_data = {"test_report": {"values": [1, 2, 3]}}
    filter_content = {
        "name": "example_report",
        "filters": ["filter1"],
        "graph_details": {"metadata_prefix": "prefix", "type": "plot"},
    }
    mock_graph_generator = mocker.patch("RUFAS.post_processing.report_generator.GraphGenerator")
    mock_graph_generator.return_value.generate_graph.return_value = []

    report_generator._prepare_report_data_to_be_graphed(graph_data, filter_content, "test_report")

    mock_graph_generator.assert_called_once_with("prefix", time=None)
    mock_graph_generator.return_value.generate_graph.assert_called_once_with(
        graph_data,
        {
            "metadata_prefix": "prefix",
            "type": "plot",
            "title": "example_report",
            "filters": ["filter1"],
            "is_aggregated_report_data": True,
        },
        "test_report",
        None,
        True,
    )


@pytest.mark.parametrize(
    "filter_content",
    [
        {"filters": ["filter1"], "graph_details": {"metadata_prefix": "prefix"}},
        {"name": "example_report", "graph_details": {"metadata_prefix": "prefix"}},
        {"name": "example_report", "filters": ["filter1"], "graph_details": {"type": "plot"}},
    ],
)
def test_prepare_report_data_to_be_graphed_missing_details(
    filter_content: dict[str, Any], report_generator: ReportGenerator, mocker: MockerFixture
) -> None:
    """Unit test for the _prepare_report_data_to_be_graphed method of ReportGenerator with missing details."""
    mock_graph_generator = mocker.patch("RUFAS.post_processing.report_generator.GraphGenerator")

    with pytest.raises(KeyError):
        report_generator._prepare_report_data_to_be_graphed({}, filter_content, "test_report")

    mock_graph_generator.return_value.generate_graph.assert_not_called()


def test_log_graph_generator_events(report_generator: ReportGenerator, mocker: MockerFixture) -> None:
    """Unit test for the _log_graph_generator_events method of ReportGenerator."""
    info_map = {"class": "GraphGenerator", "function": "generate_graph"}
    graph_event_log: list[dict[str, str | dict[str, str]]] = [
        {"log": "log name", "message": "log message", "info_map": info_map},
        {"warning": "warning name", "message": "warning message", "info_map": info_map},
        {"error": "error name", "message": "error message", "info_map": info_map},
        {"status": "success", "message": "not logged", "info_map": info_map},
        {"warning": "warning name", "error": "both", "message": "error and warning message", "info_map": info_map},
    ]
    mock_logger_log = mocker.patch.object(report_generator._logger, "log")

    report_generator._log_graph_generator_events(graph_event_log)

    assert mock_logger_log.call_args_list == [
        mocker.call(logging.INFO, "log message", extra={"rufas_name": "log name", "rufas_info_map": info_map}),
        mocker.call(
            logging.WARNING, "warning message", extra={"rufas_name": "warning name", "rufas_info_map": info_map}
        ),
        mocker.call(logging.ERROR, "error message", extra={"rufas_name": "error name", "rufas_info_map": info_map}),
        mocker.call(
            logging.ERROR, "error and warning message", extra={"rufas_name": "both", "rufas_info_map": info_map}
        ),
    ]


def test_log_graph_generator_events_without_events(report_generator: ReportGenerator, mocker: MockerFixture) -> None:
    """Unit test for the _log_graph_generator_events method of ReportGenerator when there are no events."""
    mock_logger_log = mocker.patch.object(report_generator._logger, "log")

    report_generator._log_graph_generator_events([])

    mock_logger_log.assert_not_called()


@pytest.mark.parametrize(
    "report_name, reports, expected_name",
    [
        # Case when the name is not in reports
        ("report1", {}, "report1"),
        ("report1", {"report2": {}}, "report1"),
        # Case when the name is in reports and a timestamp is appended
        ("report1", {"report1": {}}, "report1_2023-01-01"),
        # Case when the name is None
        (None, {}, "untitled_2023-01-01"),
        # Case when the name is None and the untitled name is in reports
        (None, {"untitled_2023-01-01": {}}, "untitled_2023-01-01_2023-01-01"),
        # Case when the name is empty
        ("", {}, ""),
    ],
)
def test_ensure_unique_report_name_with_timestamp(
    report_name: str | None,
    reports: dict[str, dict[str, Any]],
    expected_name: str,
    report_generator: ReportGenerator,
    mocker: MockerFixture,
) -> None:
    """Unit test for the _ensure_unique_report_name_with_timestamp method of ReportGenerator."""
    report_generator.reports = reports
    mock_get_timestamp = mocker.patch(
        "RUFAS.post_processing.report_generator.Utility.get_timestamp", return_value="2023-01-01"
    )

    result = report_generator._ensure_unique_report_name_with_timestamp(report_name)

    assert result == expected_name
    assert all(call == mocker.call(True) for call in mock_get_timestamp.call_args_list)


@pytest.mark.parametrize(
    "references, reports, expected_message",
    [
        # All references are present
        (["ref1", "ref2"], {"ref1": {}, "ref2": {}}, None),
        # One reference is missing
        (["ref1", "ref2"], {"ref1": {}}, "Missing referenced reports matching the following pattern(s): ref2"),
        # Multiple references are missing
        (
            ["ref1", "ref2", "ref3"],
            {"ref1": {}},
            "Missing referenced reports matching the following pattern(s): ref2, ref3",
        ),
        # Reports dictionary is empty
        (["ref1"], {}, "Missing referenced reports matching the following pattern(s): ref1"),
        # Regex match one reference
        (["ref\\d"], {"ref1": {}}, None),
        # Regex match multiple references
        (["ref\\d"], {"ref2": {}, "ref3": {}}, None),
        # Regex match none
        (
            ["ref\\d+"],
            {"report1": {}, "report2": {}},
            r"Missing referenced reports matching the following pattern(s): ref\\d+",
        ),
        # Partial match is not a match
        (["ref"], {"ref1": {}}, "Missing referenced reports matching the following pattern(s): ref"),
        # Complex regex pattern
        (["ref[1-3]", "report\\d{2}"], {"ref1": {}, "ref2": {}, "report01": {}}, None),
        # No references
        ([], {"ref1": {}}, None),
    ],
)
def test_check_for_missing_references(
    references: list[str],
    reports: dict[str, dict[str, Any]],
    expected_message: str | None,
    report_generator: ReportGenerator,
) -> None:
    """Unit test for the _check_for_missing_references method of ReportGenerator."""
    report_generator.reports = reports

    if expected_message is not None:
        with pytest.raises(KeyError) as excinfo:
            report_generator._check_for_missing_references(references)
        assert expected_message in str(excinfo.value)
    else:
        report_generator._check_for_missing_references(references)


@pytest.mark.parametrize(
    "regex_patterns, expected_matched_reports",
    [
        # Match single report
        (["report1"], {"report1": {"values": [1]}}),
        # Match multiple reports with simple pattern
        (["report\\d"], {"report1": {"values": [1]}, "report2": {"values": [2]}}),
        # Match multiple reports with complex pattern
        (["report[12]"], {"report1": {"values": [1]}, "report2": {"values": [2]}}),
        # Match multiple reports with multiple patterns, in the order of the patterns
        (["report2", "report1"], {"report2": {"values": [2]}, "report1": {"values": [1]}}),
        # Report matched by multiple patterns
        (["report1", "report\\d"], {"report1": {"values": [1]}, "report2": {"values": [2]}}),
        # No match
        (["unmatched"], {}),
        # Partial match not included
        (["report"], {}),
        # Match with special characters in report names
        (["special_report-\\d"], {"special_report-1": {"values": [3]}}),
        # No patterns
        ([], {}),
    ],
)
def test_get_reports_by_regex(
    regex_patterns: list[str],
    expected_matched_reports: dict[str, dict[str, list[Any]]],
    report_generator: ReportGenerator,
) -> None:
    """Unit test for the _get_reports_by_regex method of ReportGenerator."""
    report_generator.reports = {
        "report1": {"values": [1]},
        "report2": {"values": [2]},
        "special_report-1": {"values": [3]},
    }

    matched_reports = report_generator._get_reports_by_regex(regex_patterns)

    assert list(matched_reports.items()) == list(expected_matched_reports.items())


@pytest.mark.parametrize(
    "filtered_pool, filter_content, expected_report_data",
    [
        # No aggregation specified
        (
            {"col1": {"values": [1, 2, 3]}, "col2": {"values": [4, 5, 6]}},
            {"filters": [], "name": "test"},
            {"col1": [1, 2, 3], "col2": [4, 5, 6]},
        ),
        # No aggregation specified, without units displayed
        (
            {
                "col1": {"values": [1, 2, 3], "info_maps": [{"units": "dummy_units"}]},
                "col2": {"values": [4, 5, 6], "info_maps": [{"units": "dummy_units2"}]},
            },
            {"display_units": False, "filters": [], "name": "test"},
            {"col1": [1, 2, 3], "col2": [4, 5, 6]},
        ),
        # No aggregation specified, with units displayed
        (
            {
                "col1": {"values": [1, 2, 3], "info_maps": [{"units": "dummy_units"}]},
                "col2": {"values": [4, 5, 6], "info_maps": [{"units": "dummy_units2"}]},
            },
            {"display_units": True, "filters": [], "name": "test"},
            {"col1 (dummy_units)": [1, 2, 3], "col2 (dummy_units2)": [4, 5, 6]},
        ),
        # No aggregation specified, with constants
        (
            {"col1": {"values": [1, 2, 3]}, "col2": {"values": [4, 5]}},
            {"constants": {"constant": 10}, "filters": [], "name": "test"},
            {"col1": [1, 2, 3], "col2": [4, 5], "constant": [10, 10, 10]},
        ),
        # No aggregation specified, with constants and units displayed
        (
            {"col1": {"values": [1, 2], "info_maps": [{"units": "kg"}]}},
            {"constants": {"KG_TO_GRAMS": 1000}, "display_units": True, "filters": [], "name": "test"},
            {"col1 (kg)": [1, 2], "KG_TO_GRAMS_(g/kg)": [1000, 1000]},
        ),
        # Aggregation keys that are not set
        (
            {"col1": {"values": [1, 2, 3]}},
            {"horizontal_aggregation": None, "vertical_aggregation": "", "filters": [], "name": "test"},
            {"col1": [1, 2, 3]},
        ),
    ],
)
def test_perform_aggregations_without_aggregation(
    filtered_pool: dict[str, dict[str, list[Any]]],
    filter_content: dict[str, Any],
    expected_report_data: dict[str, list[Any]],
    report_generator: ReportGenerator,
    mocker: MockerFixture,
) -> None:
    """Unit test for the _perform_aggregations method of ReportGenerator when no aggregation is specified."""
    mock_route_aggregator_functions = mocker.patch.object(report_generator, "_route_aggregator_functions")

    result = report_generator._perform_aggregations(filtered_pool, filter_content)

    assert result == (expected_report_data, False)
    mock_route_aggregator_functions.assert_not_called()


@pytest.mark.parametrize(
    "filter_content, horizontal_agg_key, vertical_agg_key",
    [
        ({"horizontal_aggregation": "sum", "filters": [], "name": "test"}, "sum", None),
        ({"vertical_aggregation": "average", "filters": [], "name": "test"}, None, "average"),
        (
            {"horizontal_aggregation": "sum", "vertical_aggregation": "average", "filters": [], "name": "test"},
            "sum",
            "average",
        ),
    ],
)
def test_perform_aggregations_with_aggregation(
    filter_content: dict[str, Any],
    horizontal_agg_key: str | None,
    vertical_agg_key: str | None,
    report_generator: ReportGenerator,
    mocker: MockerFixture,
) -> None:
    """Unit test for the _perform_aggregations method of ReportGenerator when aggregations are specified."""
    filtered_pool = {"col1": {"values": [1, 2, 3]}, "col2": {"values": [4, 5, 6]}}
    aggregate_report = {"aggregated": [21]}
    mock_route_aggregator_functions = mocker.patch.object(
        report_generator, "_route_aggregator_functions", return_value=aggregate_report
    )

    result = report_generator._perform_aggregations(filtered_pool, filter_content)

    assert result == (aggregate_report, True)
    mock_route_aggregator_functions.assert_called_once_with(
        {"col1": [1, 2, 3], "col2": [4, 5, 6]}, filter_content, horizontal_agg_key, vertical_agg_key
    )


@pytest.mark.parametrize(
    "filtered_pool, filter_content, expected_message",
    [
        # Empty column
        (
            {"col1": {"values": [1, 2, 3]}, "col2": {"values": []}},
            {"filters": ["col"], "name": "test"},
            "One or more columns in the report data are empty, cannot perform aggregations.",
        ),
        # No columns
        ({}, {"filters": ["col"], "name": "test"}, r"filter \['col'\] in test led to empty report data."),
        # Invalid constant
        (
            {"col1": {"values": [1, 2, 3]}},
            {"constants": {"col1": 10}, "filters": ["col"], "name": "test"},
            "Constant name col1 already exists in report data.",
        ),
    ],
)
def test_perform_aggregations_with_error(
    filtered_pool: dict[str, dict[str, list[Any]]],
    filter_content: dict[str, Any],
    expected_message: str,
    report_generator: ReportGenerator,
) -> None:
    """Unit test for the _perform_aggregations method of ReportGenerator when the report data is not valid."""
    with pytest.raises(ValueError, match=expected_message):
        report_generator._perform_aggregations(filtered_pool, filter_content)


@pytest.mark.parametrize(
    "horizontal_agg_key, vertical_agg_key, expected_function",
    [
        ("sum", "average", "_handle_horizontal_and_vertical_aggregations"),
        ("sum", None, "_handle_horizontal_only_aggregation"),
        ("sum", "", "_handle_horizontal_only_aggregation"),
        (None, "average", "_handle_vertical_only_aggregation"),
        ("", "average", "_handle_vertical_only_aggregation"),
        (None, None, None),
    ],
)
def test_route_aggregator_functions(
    horizontal_agg_key: str | None,
    vertical_agg_key: str | None,
    expected_function: str | None,
    report_generator: ReportGenerator,
    mocker: MockerFixture,
) -> None:
    """Unit test for the _route_aggregator_functions method of ReportGenerator."""
    report_data = {"data": [1, 2, 3], "constant": [2, 2, 2]}
    filter_content = {"name": "test_report", "display_units": False}
    mock_log = mocker.patch.object(report_generator, "_log")
    mock_functions = {
        function: mocker.patch.object(report_generator, function, return_value={function: [1]})
        for function in [
            "_handle_horizontal_and_vertical_aggregations",
            "_handle_horizontal_only_aggregation",
            "_handle_vertical_only_aggregation",
        ]
    }

    result = report_generator._route_aggregator_functions(
        report_data, filter_content, horizontal_agg_key, vertical_agg_key
    )

    for function, mock_function in mock_functions.items():
        if function != expected_function:
            mock_function.assert_not_called()
    if expected_function == "_handle_horizontal_and_vertical_aggregations":
        assert result == {expected_function: [1]}
        mock_functions[expected_function].assert_called_once_with(
            report_data, horizontal_agg_key, vertical_agg_key, filter_content
        )
    elif expected_function == "_handle_horizontal_only_aggregation":
        assert result == {expected_function: [1]}
        mock_functions[expected_function].assert_called_once_with(report_data, horizontal_agg_key, filter_content)
    elif expected_function == "_handle_vertical_only_aggregation":
        assert result == {expected_function: [1]}
        mock_functions[expected_function].assert_called_once_with(report_data, vertical_agg_key, filter_content)
    else:
        assert result == report_data
    mock_log.assert_called_once_with(
        logging.INFO,
        "Report 'test_report' aggregation variables.",
        "Variables/constants aggregated: ['data', 'constant'].",
        "_route_aggregator_functions",
    )


def test_route_aggregator_functions_with_unnamed_report(
    report_generator: ReportGenerator, mocker: MockerFixture
) -> None:
    """Unit test for the _route_aggregator_functions method of ReportGenerator when the report has no name."""
    mock_log = mocker.patch.object(report_generator, "_log")

    result = report_generator._route_aggregator_functions({"data": [1, 2, 3]}, {}, vertical_agg_key="sum")

    assert result == {"ver_agg": [6]}
    mock_log.assert_called_once_with(
        logging.INFO,
        "Report 'Unnamed Report' aggregation variables.",
        "Variables/constants aggregated: ['data'].",
        "_route_aggregator_functions",
    )


@pytest.mark.parametrize(
    "report_data, horizontal_agg_key, filter_content, expected",
    [
        ({"a": [1, 2], "b": [3, 4]}, "sum", {}, {"hor_agg": [4, 6]}),
        ({"a": [1, 2], "b": [3, 4]}, "sum", {"display_units": False}, {"hor_agg": [4, 6]}),
        # Units are displayed
        ({"a (kg)": [1, 2], "b (kg)": [3, 4]}, "sum", {"display_units": True}, {"hor_agg_(kg)": [4, 6]}),
        ({"a": [1, 2], "b": [3, 4]}, "sum", {"display_units": True}, {"hor_agg_(unitless)": [4, 6]}),
        # Units are simplified by default
        (
            {"a (kg)": [8, 4], "b (kg)": [2, 1]},
            "division",
            {"display_units": True},
            {"hor_agg_(unitless)": [4.0, 4.0]},
        ),
        (
            {"a (kg)": [8, 4], "b (kg)": [2, 1]},
            "division",
            {"display_units": True, "simplify_units": False},
            {"hor_agg_(kg/kg)": [4.0, 4.0]},
        ),
        # Horizontal order
        ({"a": [8, 4], "b": [2, 1]}, "division", {}, {"hor_agg": [4.0, 4.0]}),
        ({"a": [8, 4], "b": [2, 1]}, "division", {"horizontal_order": ["b", "a"]}, {"hor_agg": [0.25, 0.25]}),
        (
            {"milk (kg)": [8, 4], "cows (animal)": [2, 1]},
            "division",
            {"horizontal_order": ["cows", "milk"], "display_units": True},
            {"hor_agg_(animal/kg)": [0.25, 0.25]},
        ),
        # Single column
        ({"data_(km)": [1, 2, 3]}, "sum", {"display_units": True}, {"hor_agg_(km)": [1, 2, 3]}),
    ],
)
def test_handle_horizontal_only_aggregation(
    report_data: dict[str, list[Any]],
    horizontal_agg_key: str,
    filter_content: dict[str, Any],
    expected: dict[str, list[Any]],
    report_generator: ReportGenerator,
) -> None:
    """Unit test for the _handle_horizontal_only_aggregation method of ReportGenerator."""
    result = report_generator._handle_horizontal_only_aggregation(report_data, horizontal_agg_key, filter_content)

    assert result == expected


def test_handle_horizontal_only_aggregation_with_unsupported_aggregator(report_generator: ReportGenerator) -> None:
    """Unit test for the _handle_horizontal_only_aggregation method of ReportGenerator with an unsupported key."""
    with pytest.raises(KeyError, match="median"):
        report_generator._handle_horizontal_only_aggregation({"a": [1, 2]}, "median", {})


@pytest.mark.parametrize(
    "report_data, vertical_agg_key, filter_content, expected",
    [
        # Multiple columns
        ({"a": [1, 2], "b": [3, 4]}, "sum", {}, {"a_ver_agg": [3], "b_ver_agg": [7]}),
        (
            {"a": [1, 2], "b": [3, 4]},
            "sum",
            {"use_verbose_report_name": True},
            {"a_ver_agg": [3], "b_ver_agg": [7]},
        ),
        # Multiple columns with units displayed
        (
            {"a (kg)": [1, 2], "b (L)": [3, 4]},
            "sum",
            {"display_units": True},
            {"a_ver_agg_(kg)": [3], "b_ver_agg_(L)": [7]},
        ),
        (
            {"a": [1, 2], "b (L)": [3, 4]},
            "average",
            {"display_units": True},
            {"a_ver_agg": [1.5], "b_ver_agg_(L)": [3.5]},
        ),
        # Single column
        ({"a": [1, 2, 3]}, "sum", {}, {"ver_agg": [6]}),
        ({"a": [1, 2, 3]}, "sum", {"display_units": False, "variables": "a"}, {"ver_agg": [6]}),
        ({"a": [1, 2, 3]}, "sum", {"use_verbose_report_name": True}, {"a_ver_agg": [6]}),
        # Single column with units displayed
        ({"a (kg)": [1, 2, 3]}, "sum", {"display_units": True}, {"ver_agg_(kg)": [6]}),
        ({"a": [1, 2, 3]}, "sum", {"display_units": True}, {"ver_agg": [6]}),
        (
            {"a (kg)": [1, 2, 3]},
            "sum",
            {"display_units": True, "use_verbose_report_name": True},
            {"a (kg)_ver_agg_(kg)": [6]},
        ),
        (
            {"a": [1, 2, 3]},
            "sum",
            {"display_units": True, "use_verbose_report_name": True},
            {"a_ver_agg": [6]},
        ),
    ],
)
def test_handle_vertical_only_aggregation(
    report_data: dict[str, list[Any]],
    vertical_agg_key: str,
    filter_content: dict[str, Any],
    expected: dict[str, list[Any]],
    report_generator: ReportGenerator,
) -> None:
    """Unit test for the _handle_vertical_only_aggregation method of ReportGenerator."""
    result = report_generator._handle_vertical_only_aggregation(report_data, vertical_agg_key, filter_content)

    assert result == expected


def test_handle_vertical_only_aggregation_with_unsupported_aggregator(report_generator: ReportGenerator) -> None:
    """Unit test for the _handle_vertical_only_aggregation method of ReportGenerator with an unsupported key."""
    with pytest.raises(KeyError, match="median"):
        report_generator._handle_vertical_only_aggregation({"a": [1, 2]}, "median", {})


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
def test_update_key(key: str, expected: str, report_generator: ReportGenerator) -> None:
    """Unit test for the _update_key method of ReportGenerator."""
    assert report_generator._update_key(key) == expected


@pytest.mark.parametrize(
    "aggregator, expected",
    [
        (Aggregator.average, "average"),
        (Aggregator.division, "division"),
        (Aggregator.product, "product"),
        (Aggregator.standard_deviation, "SD"),
        (Aggregator.sum, "sum"),
        (Aggregator.subtraction, "subtraction"),
        (Aggregator.no_op, None),
        (sum, None),
    ],
)
def test_get_aggregator_key(
    aggregator: Callable[[list[float]], float] | Callable[[list[float]], float | None],
    expected: str | None,
    report_generator: ReportGenerator,
) -> None:
    """Unit test for the _get_aggregator_key method of ReportGenerator."""
    assert report_generator._get_aggregator_key(aggregator) == expected


@pytest.mark.parametrize(
    "aggregate_report, horizontal_agg_key, vertical_agg_key, filter_content, expected",
    [
        # Horizontal first
        ({"col1": [1, 2, 3], "col2": [4, 5, 6]}, "sum", "sum", {"horizontal_first": True}, {"hor_ver_agg": [21]}),
        (
            {"col1": [1, 2, 3], "col2": [4, 5, 6]},
            "product",
            "average",
            {"horizontal_first": True, "display_units": False},
            {"hor_ver_agg": [32 / 3]},
        ),
        # Vertical first
        ({"col1": [1, 2, 3], "col2": [4, 5, 6]}, "sum", "sum", {"horizontal_first": False}, {"ver_hor_agg": [21]}),
        ({"col1": [1, 2, 3], "col2": [4, 5, 6]}, "product", "average", {}, {"ver_hor_agg": [10.0]}),
        ({"col1": [1, 2, 3], "col2": [4, 5, 6]}, "sum", "sum", {"horizontal_first": None}, {"ver_hor_agg": [21]}),
        # Horizontal first with units displayed
        (
            {"milk (kg)": [10, 20], "cows (animal)": [2, 4]},
            "division",
            "average",
            {"horizontal_first": True, "display_units": True},
            {"hor_ver_agg_(kg/animal)": [5.0]},
        ),
        (
            {"a (kg)": [8, 4], "b (kg)": [2, 1]},
            "division",
            "sum",
            {"horizontal_first": True, "display_units": True, "simplify_units": False},
            {"hor_ver_agg_(kg/kg)": [8.0]},
        ),
        # Vertical first with units displayed
        (
            {"milk (kg)": [10, 20], "cows (animal)": [2, 4]},
            "division",
            "sum",
            {"display_units": True},
            {"ver_hor_agg_(kg/animal)": [5.0]},
        ),
        (
            {"a (kg)": [8, 4], "b (kg)": [2, 1]},
            "division",
            "sum",
            {"display_units": True, "simplify_units": False},
            {"ver_hor_agg_(kg/kg)": [4.0]},
        ),
        # Horizontal order with horizontal first
        (
            {"milk": [10, 20], "cows": [2, 4]},
            "division",
            "sum",
            {"horizontal_first": True, "horizontal_order": ["cows", "milk"]},
            {"hor_ver_agg": [0.4]},
        ),
    ],
)
def test_handle_horizontal_and_vertical_aggregations(
    aggregate_report: dict[str, list[Any]],
    horizontal_agg_key: str,
    vertical_agg_key: str,
    filter_content: dict[str, Any],
    expected: dict[str, list[Any]],
    report_generator: ReportGenerator,
) -> None:
    """Unit test for the _handle_horizontal_and_vertical_aggregations method of ReportGenerator."""
    result = report_generator._handle_horizontal_and_vertical_aggregations(
        aggregate_report, horizontal_agg_key, vertical_agg_key, filter_content
    )

    assert result == expected


def test_handle_horizontal_and_vertical_aggregations_horizontal_first_calls(
    report_generator: ReportGenerator, mocker: MockerFixture
) -> None:
    """Unit test for the functions called when aggregating horizontally first."""
    aggregate_report = {"col1": [1, 2, 3], "col2": [4, 5, 6]}
    filter_content = {"horizontal_first": True, "horizontal_order": ["col2", "col1"], "simplify_units": False}
    mock_apply_horizontal_aggregation = mocker.patch.object(
        report_generator, "_apply_horizontal_aggregation", return_value=([5, 7, 9], "units")
    )
    mock_apply_vertical_aggregation = mocker.patch.object(report_generator, "_apply_vertical_aggregation")
    mock_handle_aggregation = mocker.patch.object(report_generator, "_handle_aggregation", return_value=7.0)

    result = report_generator._handle_horizontal_and_vertical_aggregations(
        aggregate_report, "sum", "average", filter_content
    )

    assert result == {"hor_ver_agg": [7.0]}
    mock_apply_horizontal_aggregation.assert_called_once_with(aggregate_report, ["col2", "col1"], Aggregator.sum, False)
    mock_handle_aggregation.assert_called_once_with(Aggregator.average, [5, 7, 9], "'col1', 'col2'")
    mock_apply_vertical_aggregation.assert_not_called()


def test_handle_horizontal_and_vertical_aggregations_vertical_first_calls(
    report_generator: ReportGenerator, mocker: MockerFixture
) -> None:
    """Unit test for the functions called when aggregating vertically first."""
    aggregate_report = {"col1": [1, 2, 3], "col2": [4, 5, 6]}
    vertically_aggregated = {"col1": [2.0], "col2": [5.0]}
    mock_apply_horizontal_aggregation = mocker.patch.object(report_generator, "_apply_horizontal_aggregation")
    mock_apply_vertical_aggregation = mocker.patch.object(
        report_generator, "_apply_vertical_aggregation", return_value=vertically_aggregated
    )
    mock_handle_aggregation = mocker.patch.object(report_generator, "_handle_aggregation", return_value=7.0)
    mock_aggregate_units = mocker.patch.object(report_generator.unit_handler, "aggregate_units", return_value="units")

    result = report_generator._handle_horizontal_and_vertical_aggregations(
        aggregate_report, "sum", "average", {"display_units": True}
    )

    assert result == {"ver_hor_agg_(units)": [7.0]}
    mock_apply_vertical_aggregation.assert_called_once_with(aggregate_report, Aggregator.average)
    mock_handle_aggregation.assert_called_once_with(Aggregator.sum, [2.0, 5.0], "'col1', 'col2'")
    mock_aggregate_units.assert_called_once_with(vertically_aggregated, "sum", True)
    mock_apply_horizontal_aggregation.assert_not_called()


@pytest.mark.parametrize(
    "horizontal_agg_key, vertical_agg_key",
    [("median", "sum"), ("sum", "median")],
)
def test_handle_horizontal_and_vertical_aggregations_with_unsupported_aggregator(
    horizontal_agg_key: str, vertical_agg_key: str, report_generator: ReportGenerator
) -> None:
    """Unit test for the _handle_horizontal_and_vertical_aggregations method with an unsupported key."""
    with pytest.raises(KeyError, match="median"):
        report_generator._handle_horizontal_and_vertical_aggregations(
            {"a": [1, 2]}, horizontal_agg_key, vertical_agg_key, {}
        )


@pytest.mark.parametrize(
    "filter_content, expected_horizontal, expected_vertical",
    [
        # Test with valid horizontal and vertical keys
        ({"horizontal_aggregation": "sum", "vertical_aggregation": "average"}, "sum", "average"),
        # Test with valid horizontal key and no vertical key
        ({"horizontal_aggregation": "product"}, "product", None),
        # Test with no horizontal key and valid vertical key
        ({"vertical_aggregation": "division"}, None, "division"),
        # Test with empty filter content
        ({}, None, None),
    ],
)
def test_extract_aggregation_keys(
    filter_content: dict[str, Any],
    expected_horizontal: str | None,
    expected_vertical: str | None,
    report_generator: ReportGenerator,
) -> None:
    """Unit test for the _extract_aggregation_keys method of ReportGenerator."""
    assert report_generator._extract_aggregation_keys(filter_content) == (expected_horizontal, expected_vertical)


@pytest.mark.parametrize(
    "report_data, loop_list, aggregator_key, expected",
    [
        # Tests with sum aggregation
        ({"a": [1, 2], "b": [3, 4]}, ["a", "b"], "sum", ([4, 6], "unitless")),
        ({"a": [1, 2, 3], "b": [4, 5, 6]}, ["a", "b"], "sum", ([5, 7, 9], "unitless")),
        # Tests with subtraction aggregation
        ({"a": [1, 2], "b": [3, 4]}, ["a", "b"], "subtraction", ([-2, -2], "unitless")),
        ({"a": [1, 2, 3], "b": [4, 5, 6]}, ["a", "b"], "subtraction", ([-3, -3, -3], "unitless")),
        # Tests with product aggregation
        ({"a": [1, 2], "b": [3, 4]}, ["a", "b"], "product", ([3, 8], "unitless")),
        ({"a": [1, 2, 3], "b": [4, 5, 6]}, ["a", "b"], "product", ([4, 10, 18], "unitless")),
        # Tests with division aggregation
        ({"a": [1, 2], "b": [3, 4]}, ["a", "b"], "division", ([0.3333333333333333, 0.5], "unitless")),
        ({"a": [1, 2, 3], "b": [4, 5, 6]}, ["a", "b"], "division", ([0.25, 0.4, 0.5], "unitless")),
        # Tests with average aggregation
        ({"a": [1, 3], "b": [2, 4]}, ["a", "b"], "average", ([1.5, 3.5], "unitless")),
        ({"a": [1, 2, 3], "b": [4, 5, 6]}, ["a", "b"], "average", ([2.5, 3.5, 4.5], "unitless")),
        # Tests with standard deviation aggregation
        ({"a": [10, 10], "b": [20, 20]}, ["a", "b"], "SD", ([5.0, 5.0], "unitless")),
        ({"a": [10, 12, 23, 23], "b": [17, 15, 22, 20]}, ["a", "b"], "SD", ([3.5, 1.5, 0.5, 1.5], "unitless")),
        # Tests with the order of the columns
        ({"a": [1, 2], "b": [3, 4]}, ["b", "a"], "division", ([3.0, 2.0], "unitless")),
        ({"x (kg)": [1, 2], "y (day)": [3, 4]}, ["y", "x"], "division", ([3.0, 2.0], "day/kg")),
        # Tests with columns that are not aggregated
        ({"a": [1, 2], "b": [3, 4], "c": [5, 6]}, ["a", "c"], "sum", ([6, 8], "unitless")),
        ({"a": [1, 2], "b": [3, 4, 5], "c": [5, 6]}, ["a", "c"], "sum", ([6, 8], "unitless")),
        # Tests with columns selected by a part of their names
        (
            {"pen_1.milk": [1, 2], "pen_2.milk": [3, 4], "cows": [2, 2]},
            ["milk", "cows"],
            "division",
            ([1 / 3 / 2, 2 / 4 / 2], ""),
        ),
        # Tests with units
        ({"a (kg)": [1, 2], "b (kg)": [3, 4]}, ["a", "b"], "sum", ([4, 6], "kg")),
        ({"milk (kg)": [1, 2], "cows (animal)": [4, 4]}, ["milk", "cows"], "division", ([0.25, 0.5], "kg/animal")),
        # Tests with values that cannot be aggregated
        ({"a": [1, None], "b": [3, 4]}, ["a", "b"], "sum", ([4, None], "unitless")),
    ],
)
def test_apply_horizontal_aggregation(
    report_data: dict[str, list[Any]],
    loop_list: list[str],
    aggregator_key: str,
    expected: tuple[list[Any], str],
    report_generator: ReportGenerator,
    mocker: MockerFixture,
) -> None:
    """Unit test for the _apply_horizontal_aggregation method of ReportGenerator."""
    mocker.patch.object(report_generator, "_log")

    result = report_generator._apply_horizontal_aggregation(
        report_data, loop_list, AGGREGATION_FUNCTIONS[aggregator_key], True
    )

    assert result == expected


@pytest.mark.parametrize(
    "report_data, loop_list",
    [
        # Inconsistent lengths
        ({"a": [1, 2, 3], "b": [3, 4]}, ["a", "b"]),
        # No columns to aggregate
        ({"a": [1, 2, 3], "b": [3, 4, 5]}, ["c"]),
        ({"a": [1, 2, 3], "b": [3, 4, 5]}, []),
    ],
)
def test_apply_horizontal_aggregation_with_error(
    report_data: dict[str, list[Any]], loop_list: list[str], report_generator: ReportGenerator
) -> None:
    """Unit test for the _apply_horizontal_aggregation method of ReportGenerator when data cannot be aggregated."""
    with pytest.raises(ValueError, match="Can't aggregate data with different lengths"):
        report_generator._apply_horizontal_aggregation(report_data, loop_list, AGGREGATION_FUNCTIONS["sum"], True)


def test_apply_horizontal_aggregation_calls(report_generator: ReportGenerator, mocker: MockerFixture) -> None:
    """Unit test for the functions called by the _apply_horizontal_aggregation method of ReportGenerator."""
    report_data = {"a": [1, 2], "b": [3, 4], "c": [5, 6]}
    mock_handle_aggregation = mocker.patch.object(report_generator, "_handle_aggregation", side_effect=[10.0, 20.0])
    mock_aggregate_units = mocker.patch.object(report_generator.unit_handler, "aggregate_units", return_value="units")

    result = report_generator._apply_horizontal_aggregation(report_data, ["c", "a"], Aggregator.division, False)

    assert result == ([10.0, 20.0], "units")
    assert mock_handle_aggregation.call_args_list == [
        mocker.call(Aggregator.division, [5, 1], "'a', 'b', 'c'"),
        mocker.call(Aggregator.division, [6, 2], "'a', 'b', 'c'"),
    ]
    mock_aggregate_units.assert_called_once_with({"c": [5, 6], "a": [1, 2]}, "division", False)
    assert list(mock_aggregate_units.call_args.args[0].keys()) == ["c", "a"]


@pytest.mark.parametrize(
    "report_data, aggregator_key, expected",
    [
        # Tests with sum aggregator
        ({"a": [1, 2], "b": [3, 4]}, "sum", {"a": [3], "b": [7]}),
        ({"a": [1, 2, 3], "b": [4, 5, 6]}, "sum", {"a": [6], "b": [15]}),
        # Tests with subtraction aggregator
        ({"a": [1, 2], "b": [3, 4]}, "subtraction", {"a": [-1], "b": [-1]}),
        # Tests with product aggregator
        ({"a": [1, 2], "b": [3, 4]}, "product", {"a": [2], "b": [12]}),
        ({"a": [1, 2, 3], "b": [4, 5, 6]}, "product", {"a": [6], "b": [120]}),
        # Tests with average aggregator
        ({"a": [1, 2, 3], "b": [4, 5, 6]}, "average", {"a": [2.0], "b": [5.0]}),
        ({"a": [1, 2, 3, 4], "b": [5, 6, 7, 8]}, "average", {"a": [2.5], "b": [6.5]}),
        # Tests with division aggregator
        ({"a": [8, 4], "b": [2, 1]}, "division", {"a": [2.0], "b": [2.0]}),
        ({"a": [8, 4, 2], "b": [2, 1, 1]}, "division", {"a": [1.0], "b": [2.0]}),
        # Tests with standard deviation aggregator
        (
            {"a": [10, 12, 23, 23], "b": [17, 15, 22, 20]},
            "SD",
            {"a": [6.041522986797286], "b": [2.692582403567252]},
        ),
        # Tests with columns of different lengths
        ({"a": [1, 2, 3], "b": [4]}, "sum", {"a": [6], "b": [4]}),
        # Tests with values that cannot be aggregated
        ({"a": [1, None], "b": [3, 4]}, "sum", {"a": [None], "b": [7]}),
        # Tests with aggregations that cannot be done
        ({"a": [1], "b": [3, 0]}, "division", {"a": [None], "b": [None]}),
        # Tests with no columns
        ({}, "sum", {}),
    ],
)
def test_apply_vertical_aggregation(
    report_data: dict[str, list[Any]],
    aggregator_key: str,
    expected: dict[str, list[Any]],
    report_generator: ReportGenerator,
    mocker: MockerFixture,
) -> None:
    """Unit test for the _apply_vertical_aggregation method of ReportGenerator."""
    mocker.patch.object(report_generator, "_log")

    result = report_generator._apply_vertical_aggregation(report_data, AGGREGATION_FUNCTIONS[aggregator_key])

    assert result == expected


def test_apply_vertical_aggregation_calls(report_generator: ReportGenerator, mocker: MockerFixture) -> None:
    """Unit test for the functions called by the _apply_vertical_aggregation method of ReportGenerator."""
    mock_handle_aggregation = mocker.patch.object(report_generator, "_handle_aggregation", side_effect=[3, None])

    result = report_generator._apply_vertical_aggregation({"a": [1, 2], "b": [3, None]}, Aggregator.sum)

    assert result == {"a": [3], "b": [None]}
    assert mock_handle_aggregation.call_args_list == [
        mocker.call(Aggregator.sum, [1, 2], "a"),
        mocker.call(Aggregator.sum, [3, None], "b"),
    ]


@pytest.mark.parametrize(
    "aggregator, data, expected_result",
    [
        # Valid data: normal floats
        (sum, [1.0, 2.0, 3.0], 6.0),
        # Empty list
        (sum, [], 0),
        # NumPy floats
        (sum, [np.float64(1.0), np.float64(2.0), np.float64(3.0)], 6.0),
        # NumPy ints
        (sum, [np.int64(1), np.int64(2), np.int64(3)], 6),
        # Bools (bool is a subclass of int)
        (sum, [True, False, 1.0], 2.0),
        # Aggregator returning None
        (Aggregator.division, [1.0], None),
        (Aggregator.division, [1.0, 0.0], None),
    ],
)
def test_handle_aggregation(
    aggregator: Callable[[list[float]], float] | Callable[[list[float]], float | None],
    data: list[Any],
    expected_result: float | None,
    report_generator: ReportGenerator,
    mocker: MockerFixture,
) -> None:
    """Unit test for the _handle_aggregation method of ReportGenerator."""
    mock_log = mocker.patch.object(report_generator, "_log")

    result = report_generator._handle_aggregation(aggregator, data, "valid_key")

    assert result == expected_result
    mock_log.assert_not_called()


@pytest.mark.parametrize(
    "data",
    [
        # None in data
        [1.0, None, 3.0],
        # NaN in data
        [1.0, float("nan"), 3.0],
        [1.0, np.nan, 3.0],
        # Complex in data
        [1.0, 2.0, complex(1, 1)],
        # String in data
        [1.0, "a", 3.0],
        # Dictionary in data
        [{"a": 1.0}, {"a": 2.0}],
    ],
)
def test_handle_aggregation_with_unaggregatable_values(
    data: list[Any], report_generator: ReportGenerator, mocker: MockerFixture
) -> None:
    """Unit test for the _handle_aggregation method of ReportGenerator when data has values it cannot aggregate."""
    mock_log = mocker.patch.object(report_generator, "_log")
    mock_aggregator = mocker.MagicMock()

    result = report_generator._handle_aggregation(mock_aggregator, data, "invalid_key")

    assert result is None
    mock_aggregator.assert_not_called()
    mock_log.assert_called_once_with(
        logging.ERROR,
        "ReportGenerator aggregation error",
        "Encountered unaggregatable values in variable(s): invalid_key. Returning None instead.",
        "_handle_aggregation",
    )


def test_handle_aggregation_with_aggregator_error(report_generator: ReportGenerator, mocker: MockerFixture) -> None:
    """Unit test for the _handle_aggregation method of ReportGenerator when the aggregator raises an error."""
    mock_log = mocker.patch.object(report_generator, "_log")

    result = report_generator._handle_aggregation(lambda x: x[0] / 0, [1.0, 2.0, 3.0], "key")

    assert result is None
    mock_log.assert_called_once_with(
        logging.ERROR,
        "ReportGenerator aggregation error",
        "Error during aggregation of key data: float division by zero, returning None instead.",
        "_handle_aggregation",
    )


@pytest.mark.parametrize(
    "report_data, filter_content, expected_report_data",
    [
        # Valid case with a valid constant
        (
            {"existing_data": [1, 2, 3]},
            {"constants": {"Constant1": 10}},
            {"existing_data": [1, 2, 3], "Constant1": [10, 10, 10]},
        ),
        # Valid case with multiple constants
        (
            {"existing_data": [1, 2]},
            {"constants": {"Constant1": 10, "Constant2": 2.5}, "display_units": False},
            {"existing_data": [1, 2], "Constant1": [10, 10], "Constant2": [2.5, 2.5]},
        ),
        # Valid case with existing data of different lengths
        (
            {"col1": [1, 2, 3], "col2": [4, 5, 6, 7]},
            {"constants": {"Constant1": 10}},
            {"col1": [1, 2, 3], "col2": [4, 5, 6, 7], "Constant1": [10, 10, 10, 10]},
        ),
        # Valid cases with no constants
        ({"existing_data": [1, 2, 3]}, {}, {"existing_data": [1, 2, 3]}),
        ({"existing_data": [1, 2, 3]}, {"constants": {}}, {"existing_data": [1, 2, 3]}),
        ({"existing_data": [1, 2, 3]}, {"constants": None, "display_units": True}, {"existing_data": [1, 2, 3]}),
    ],
)
def test_add_constants_to_report_data(
    report_data: dict[str, list[Any]],
    filter_content: dict[str, Any],
    expected_report_data: dict[str, list[Any]],
    report_generator: ReportGenerator,
    mocker: MockerFixture,
) -> None:
    """Unit test for the _add_constants_to_report_data method of ReportGenerator."""
    mock_add_units_to_constants = mocker.patch.object(report_generator.unit_handler, "add_units_to_constants")

    report_generator._add_constants_to_report_data(report_data, filter_content)

    assert report_data == expected_report_data
    mock_add_units_to_constants.assert_not_called()


def test_add_constants_to_report_data_with_units(report_generator: ReportGenerator, mocker: MockerFixture) -> None:
    """Unit test for the _add_constants_to_report_data method of ReportGenerator when units are displayed."""
    report_data = {"existing_data (kg)": [1, 2, 3]}
    constants_config = {"Constant1": 10}
    mock_add_units_to_constants = mocker.patch.object(
        report_generator.unit_handler, "add_units_to_constants", return_value={"Constant1_(units)": 10}
    )

    report_generator._add_constants_to_report_data(report_data, {"constants": constants_config, "display_units": True})

    assert report_data == {"existing_data (kg)": [1, 2, 3], "Constant1_(units)": [10, 10, 10]}
    mock_add_units_to_constants.assert_called_once_with(constants_config)


@pytest.mark.parametrize(
    "report_data, filter_content",
    [
        # Error case with a constant name that already exists in report_data
        ({"Constant1": [5, 5, 5]}, {"constants": {"Constant1": 10}}),
        # Error case with a constant that is not a number
        ({"existing_data": [1, 2, 3]}, {"constants": {"Constant1": "ten"}}),
        # Error case with no data
        ({}, {"constants": {"Constant1": 10}}),
    ],
)
def test_add_constants_to_report_data_with_error(
    report_data: dict[str, list[Any]], filter_content: dict[str, Any], report_generator: ReportGenerator
) -> None:
    """Unit test for the _add_constants_to_report_data method of ReportGenerator when constants cannot be added."""
    expected_report_data = dict(report_data)

    with pytest.raises(ValueError):
        report_generator._add_constants_to_report_data(report_data, filter_content)

    assert report_data == expected_report_data


@pytest.mark.parametrize(
    "report_data, constant_config, expected_message",
    [
        # Valid case with valid constants
        ({}, {"Constant1": 10, "Constant2": 20.5}, None),
        ({"existing_data": [1, 2, 3]}, {"Constant1": 0, "Constant2": -20.5}, None),
        # Valid case with no constants
        ({"existing_data": [1, 2, 3]}, {}, None),
        # Error case with repeated constant name
        ({"Constant1": [5, 5, 5]}, {"Constant1": 10}, "Constant name Constant1 already exists in report data."),
        # Error case with constant name None
        ({}, {None: 10}, "Constant name cannot be None."),
        # Error case with constant value None
        ({}, {"Constant1": None}, "Constant value cannot be None."),
        # Error case with constant name not a string
        ({}, {123: 10}, "Constant name 123 must be a string and cannot be empty."),
        # Error case with constant value not a number
        ({}, {"Constant1": "not_a_number"}, "Constant value not_a_number must be a number."),
        # Error case with an empty constant name
        ({}, {"": 10}, "Constant name  cannot be empty."),
        # Error case with a valid constant followed by one that is not valid
        ({}, {"Constant1": 10, "Constant2": None}, "Constant value cannot be None."),
    ],
)
def test_validate_constants(
    report_data: dict[str, list[Any]],
    constant_config: dict[Any, Any],
    expected_message: str | None,
    report_generator: ReportGenerator,
) -> None:
    """Unit test for the _validate_constants method of ReportGenerator."""
    if expected_message is not None:
        with pytest.raises(ValueError) as excinfo:
            report_generator._validate_constants(report_data, constant_config)
        assert str(excinfo.value) == f"Report Generator error: {expected_message}"
    else:
        report_generator._validate_constants(report_data, constant_config)

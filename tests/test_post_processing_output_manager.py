from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, PropertyMock

import pytest
from pytest_mock import MockerFixture

from RUFAS.post_processing.output_manager import OutputManager
from RUFAS.post_processing.shared_data_types import E2E_REPORT_FILTERS_KEY

REPORT_FILTERS: list[dict[str, Any]] = [
    {"name": "x_sum", "filters": ["A.x"], "vertical_aggregation": "sum"},
    {"name": "x_sum_doubled", "cross_references": ["x_sum.*"], "horizontal_aggregation": "sum"},
]


@pytest.fixture
def output_manager(mocker: MockerFixture) -> OutputManager:
    """Returns the new OutputManager with its logging methods stubbed out."""
    om = OutputManager()
    mocker.patch.object(om, "add_log")
    mocker.patch.object(om, "add_warning")
    mocker.patch.object(om, "add_error")
    return om


def mock_report_generator(mocker: MockerFixture, reports: dict[str, dict[str, list[Any]]]) -> MagicMock:
    """Patches the ReportGenerator used by the OutputManager and returns the instance it creates."""
    report_generator = MagicMock()
    report_generator.reports = reports
    mocker.patch("RUFAS.post_processing.output_manager.ReportGeneratorConfig")
    mocker.patch("RUFAS.post_processing.output_manager.ReportGenerator", return_value=report_generator)
    return report_generator


@pytest.mark.parametrize("is_end_to_end_testing_run", [True, False])
def test_route_save_functions_json_with_report_filters(
    mocker: MockerFixture, output_manager: OutputManager, is_end_to_end_testing_run: bool
) -> None:
    """Tests that report filters of a JSON filter only add aggregated results during end-to-end testing."""
    mocker.patch.object(output_manager, "is_end_to_end_testing_run", is_end_to_end_testing_run)
    mocker.patch.object(output_manager, "is_first_post_processing", True)
    mocker.patch.object(
        type(output_manager), "_filter_prefixes", new_callable=PropertyMock, return_value={"json": "e2e_json_"}
    )
    mocker.patch.object(output_manager.file_manager, "create_directory")
    save_to_json = mocker.patch.object(output_manager.file_manager, "save_to_json")
    aggregated_pool = {"raw": {"values": [0]}, "x_sum_ver_agg": {"values": [6]}}
    add_aggregated_results = mocker.patch.object(
        output_manager, "_add_e2e_aggregated_results", return_value=aggregated_pool
    )
    filter_file = "e2e_json_file.json"
    json_dir = Path("json_dir")
    filtered_pool = {"raw": {"values": [0]}}
    filter_content = {"name": "e2e", "filters": ["raw"], E2E_REPORT_FILTERS_KEY: REPORT_FILTERS}

    output_manager._route_save_functions(
        filter_file, filtered_pool, True, filter_content, json_dir, Path("graphics_dir"), Path("csv_dir"), None
    )

    if is_end_to_end_testing_run:
        add_aggregated_results.assert_called_once_with(filtered_pool, filter_content, filter_file)
        save_to_json.assert_called_once_with(filter_file, json_dir, aggregated_pool, filter_content)
    else:
        add_aggregated_results.assert_not_called()
        save_to_json.assert_called_once_with(filter_file, json_dir, filtered_pool, filter_content)


def test_add_e2e_aggregated_results(mocker: MockerFixture, output_manager: OutputManager) -> None:
    """Tests that report filters are generated in order and their columns combined with the raw variables."""
    report_generator = mock_report_generator(
        mocker, {"x_sum_ver_agg": {"values": [6]}, "x_sum_doubled_hor_agg": {"values": [6]}}
    )
    x_pool = {"A.x": {"values": [1, 2, 3]}}
    filter_variables_pool = mocker.patch.object(output_manager, "filter_variables_pool", return_value=x_pool)
    filtered_pool = {"raw": {"values": [0]}}

    result = output_manager._add_e2e_aggregated_results(
        filtered_pool, {E2E_REPORT_FILTERS_KEY: REPORT_FILTERS}, "e2e_json_file.json"
    )

    assert result == {
        "raw": {"values": [0]},
        "x_sum_ver_agg": {"values": [6]},
        "x_sum_doubled_hor_agg": {"values": [6]},
    }
    assert filtered_pool == {"raw": {"values": [0]}}
    filter_variables_pool.assert_called_once_with(REPORT_FILTERS[0])
    assert report_generator.generate_report.call_args_list == [
        mocker.call(REPORT_FILTERS[0], x_pool),
        mocker.call(REPORT_FILTERS[1], {}),
    ]
    output_manager.add_error.assert_not_called()  # type: ignore[attr-defined]


def test_add_e2e_aggregated_results_skips_invalid_and_colliding_reports(
    mocker: MockerFixture, output_manager: OutputManager
) -> None:
    """Tests that non-object report filters and report columns named like a raw variable are left out with errors."""
    report_generator = mock_report_generator(mocker, {"raw": {"values": [5]}})
    mocker.patch.object(output_manager, "filter_variables_pool", return_value={"A.y": {"values": [4, 5, 6]}})
    report_filter = {"name": "raw", "filters": ["A.y"]}

    result = output_manager._add_e2e_aggregated_results(
        {"raw": {"values": [0]}}, {E2E_REPORT_FILTERS_KEY: ["not a filter", report_filter]}, "e2e_json_file.json"
    )

    assert result == {"raw": {"values": [0]}}
    report_generator.generate_report.assert_called_once_with(report_filter, {"A.y": {"values": [4, 5, 6]}})
    add_error = output_manager.add_error
    assert add_error.call_count == 2  # type: ignore[attr-defined]
    assert "must be JSON objects" in add_error.call_args_list[0].args[1]  # type: ignore[attr-defined]
    assert "same name as a variable" in add_error.call_args_list[1].args[1]  # type: ignore[attr-defined]

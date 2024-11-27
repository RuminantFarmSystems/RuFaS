from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from RUFAS.e2e_test_results_comparer import E2ETestResultsComparer, ResultPathType


@pytest.mark.parametrize("diff,successful", [({}, True), ({"diff": "diff"}, False)])
def test_compare_simulation_outputs_to_expected_outputs(
    mocker: MockerFixture,
    diff: dict[str, str],
    successful: bool,
) -> None:
    """Tests _compare_simulation_outputs_to_expected_outputs in TaskManager."""
    json_dir_path: Path = Path("json_dir")
    mocker.patch("RUFAS.e2e_test_results_comparer.OutputManager.__init__", return_value=None)
    results_path = ResultPathType("test_domain", "expected_results", "actual_results")
    get_result_paths = mocker.patch.object(
        E2ETestResultsComparer, "_get_test_result_paths", return_value=[results_path]
    )
    mocker.patch(
        "pathlib.Path.iterdir",
        return_value=[
            Path("not/the/path"),
            Path("json_dir/actual_results.json"),
            Path("not/the/path/either"),
        ],
    )
    mocked_open = mocker.patch("builtins.open", mocker.mock_open(read_data="file contents"))
    mocked_load = mocker.patch("json.load", side_effect=[{"a": 1}, {"expected_results": {"a": 1}}])
    mocked_deepdiff = mocker.patch("RUFAS.e2e_test_results_comparer.DeepDiff", return_value=diff)
    add_log = mocker.patch("RUFAS.e2e_test_results_comparer.OutputManager.add_log")
    add_error = mocker.patch("RUFAS.e2e_test_results_comparer.OutputManager.add_error")
    add_var = mocker.patch("RUFAS.e2e_test_results_comparer.OutputManager.add_variable")

    E2ETestResultsComparer.compare_actual_and_expected_test_results(json_dir_path)

    get_result_paths.assert_called_once()
    assert mocked_open.call_count == 2
    assert mocked_load.call_count == 2
    mocked_deepdiff.assert_called_once()
    if successful:
        assert add_log.call_count == 2
        assert add_error.call_count == 0
        assert add_var.call_count == 1
    else:
        assert add_log.call_count == 1
        assert add_error.call_count == 1
        assert add_var.call_count == 2


def test_get_test_results_paths(mocker: MockerFixture) -> None:
    """Tests that paths for gathering end-to-end test results are processed correctly."""
    get_data = mocker.patch(
        "RUFAS.e2e_test_results_comparer.InputManager.get_data",
        return_value=[
            {"domain": "one", "expected_results_path": "expected_1", "actual_results_path": "actual_1"},
            {"domain": "two", "expected_results_path": "expected_2", "actual_results_path": "actual_2"},
        ],
    )
    expected = [ResultPathType("one", "expected_1", "actual_1"), ResultPathType("two", "expected_2", "actual_2")]

    actual = E2ETestResultsComparer._get_test_result_paths()

    assert actual == expected
    get_data.assert_called_once_with("end_to_end_testing_result_paths.end_to_end_test_result_paths")


def mock_diff_result() -> dict[str, dict[str, dict[str, float]]]:
    """Return a mock DeepDiff result for testing."""
    return {
        "values_changed": {
            "key1": {"old_value": 100.0, "new_value": 100.0001},
            "key2": {"old_value": 50.0, "new_value": 51.0},
            "nested_key": {
                "nested": {
                    "key3": {"old_value": 200.0, "new_value": 200.0000001},
                    "key4": {"old_value": 30.0, "new_value": 40.0},
                }
            },
        }
    }


@pytest.mark.parametrize(
    "diff_result, tolerance, expected_keys",
    [
        # Case 1: Basic functionality
        (
            {
                "values_changed": {
                    "key1": {"old_value": 100.0, "new_value": 100.0001},
                    "key2": {"old_value": 50.0, "new_value": 51.0},
                }
            },
            1e-3,
            {"key2"},
        ),
        # Case 2: Nested dictionary
        (
            {
                "values_changed": {
                    "nested_key": {
                        "nested": {
                            "key3": {"old_value": 200.0, "new_value": 200.0000001},
                            "key4": {"old_value": 30.0, "new_value": 40.0},
                        }
                    }
                }
            },
            1e-7,
            {"nested_key"},
        ),
        # Case 3: Empty nested dictionary
        (
            {
                "values_changed": {
                    "nested_key": {
                        "nested": {
                            "key1": {"old_value": 10.0, "new_value": 10.000001},
                            "key2": {"old_value": 20.0, "new_value": 20.000001},
                        }
                    }
                }
            },
            1e-5,
            set(),
        ),
        # Case 4: Boundary tolerance
        (
            {
                "values_changed": {
                    "key1": {"old_value": 10.0, "new_value": 10.000001},
                    "key2": {"old_value": 10.0, "new_value": 10.00001},
                    "key3": {"old_value": 10.0, "new_value": 10.0001},
                }
            },
            1e-5,
            {"key3"},
        ),
        # Case 5: Non-numeric and missing keys
        (
            {
                "values_changed": {
                    "key1": {"old_value": "a", "new_value": "b"},
                    "key2": {"old_value": 10.0},
                    "key3": {"new_value": 20.0},
                    "key4": {},
                }
            },
            1e-3,
            {"key1", "key2", "key3"},
        ),
    ],
)
def test_filter_insignificant_changes(diff_result: dict[str, dict[str, dict[str, float | str]]],
                                      tolerance: float, expected_keys: set[str]) -> None:
    """Parameterized test for filter_insignificant_changes."""
    filtered_result = E2ETestResultsComparer.filter_insignificant_changes(diff_result, tolerance)
    remaining_keys = set(filtered_result["values_changed"].keys())

    # Assert
    assert remaining_keys == expected_keys

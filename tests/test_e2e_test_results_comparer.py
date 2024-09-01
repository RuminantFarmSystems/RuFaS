import pytest

from pytest_mock import MockerFixture
from pathlib import Path

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

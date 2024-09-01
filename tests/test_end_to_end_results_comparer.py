import pytest

from pytest_mock import MockerFixture
from pathlib import Path

from RUFAS.end_to_end_test_results_comparer import EndToEndTestResultsComparer, ResultPathType


@pytest.mark.parametrize("diff,successful", [({}, True), ({"diff": "diff"}, False)])
def test_compare_simulation_outputs_to_expected_outputs(
    mocker: MockerFixture,
    diff: dict[str, str],
    successful: bool,
) -> None:
    """Tests _compare_simulation_outputs_to_expected_outputs in TaskManager."""
    json_dir_path: Path = Path("json_dir")
    mocker.patch("RUFAS.end_to_end_test_results_comparer.OutputManager.__init__", return_value=None)
    results_path = ResultPathType("test_domain", "expected_results", "actual_results")
    get_result_paths = mocker.patch.object(EndToEndTestResultsComparer, "_get_test_result_paths", return_value=[
        results_path
    ])
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
    mocked_deepdiff = mocker.patch("RUFAS.end_to_end_test_results_comparer.DeepDiff", return_value=diff)
    add_log = mocker.patch("RUFAS.end_to_end_test_results_comparer.OutputManager.add_log")
    add_error = mocker.patch("RUFAS.end_to_end_test_results_comparer.OutputManager.add_error")
    add_var = mocker.patch("RUFAS.end_to_end_test_results_comparer.OutputManager.add_variable")

    EndToEndTestResultsComparer.compare_actual_and_expected_test_results(json_dir_path)

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

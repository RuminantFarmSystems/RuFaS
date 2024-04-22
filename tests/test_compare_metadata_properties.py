import json
import pytest
from unittest.mock import MagicMock, mock_open, patch
from compare_metadata_properties import load_json, compare_metadata_properties


def test_load_json_success():
    """Test loading a valid JSON file."""
    mock_data = '{"name": "test"}'
    with patch("builtins.open", mock_open(read_data=mock_data)):
        with patch("json.load", return_value=json.loads(mock_data)) as mock_json_load:
            result = load_json("fake_path.json")
            mock_json_load.assert_called_once()
            assert result == {"name": "test"}, "Should return parsed JSON"


@pytest.mark.parametrize(
    "error, file_name",
    [(FileNotFoundError, "nonexistent.json"), (PermissionError, "restricted.json"), (OSError, "error.json")],
)
def test_load_json_errors(error, file_name):
    """Test error handling for various file errors in load_json."""
    with patch("builtins.open", side_effect=error):
        result = load_json(file_name)
        assert result is None, f"Should return None when {error.__name__} occurs"


def test_compare_metadata_properties():
    """Test basic functionality of comparing two JSON files."""
    test_args = ["script_name", "file1.json", "file2.json"]
    with patch("sys.argv", test_args):
        with patch(
            "argparse.ArgumentParser.parse_args", return_value=MagicMock(file1="file1.json", file2="file2.json")
        ):
            with patch(
                "compare_metadata_properties.load_json",
                side_effect=[{"key": "value1"}, {"key": "value2", "key2": "value3"}],
            ):
                with patch("deepdiff.DeepDiff") as mock_deepdiff:
                    mock_deepdiff.return_value = {
                        "dictionary_item_added": {"root['key2']": "value3"},
                        "values_changed": {"root['key']": {"new_value": "value2", "old_value": "value1"}},
                    }
                    with patch("pprint.pformat", return_value="diff_output"):
                        with patch("builtins.open", mock_open()) as mock_file:
                            compare_metadata_properties()
                            mock_file.assert_called_with("output/diff_results_file1.json_vs_file2.json.txt", "w")
                            mock_file().write.assert_called()


@pytest.mark.parametrize(
    "error, function_to_patch, expected_message",
    [
        (
            FileNotFoundError,
            "builtins.open",
            "Error: The directory 'output' does not exist or diff_results_file1.json_vs_file2.json.txt "
            "cannot be accessed.",
        ),
        (
            PermissionError,
            "builtins.open",
            "Error: Permission denied when trying to write to diff_results_file1.json_vs_file2.json.txt.",
        ),
        (OSError, "builtins.open", "An unexpected OS error occurred:"),
    ],
)
def test_compare_metadata_properties_file_handling_errors(error, function_to_patch, expected_message, capsys):
    """
    Test error handling for file errors during the write process in compare_metadata_properties.
    """
    test_args = ["script_name", "file1.json", "file2.json"]
    with patch("sys.argv", test_args):
        with patch(
            "argparse.ArgumentParser.parse_args", return_value=MagicMock(file1="file1.json", file2="file2.json")
        ):
            with patch("compare_metadata_properties.load_json", return_value={"key": "value"}):
                with patch("deepdiff.DeepDiff", return_value={"differences": "diff_output"}):
                    with patch("pprint.pformat", return_value="diff_output"):
                        with patch(function_to_patch, side_effect=error):
                            compare_metadata_properties()
                            captured = capsys.readouterr()
                            assert expected_message in captured.out

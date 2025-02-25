import json
from collections import namedtuple
from pathlib import Path
import shutil
from typing import Any

from deepdiff import DeepDiff

from RUFAS.general_constants import GeneralConstants
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.units import MeasurementUnits
from RUFAS.util import Utility

ResultPathType = namedtuple("ResultPathType", ["domain", "expected_results_path", "actual_results_path", "tolerance"])
ORDERED_EXPECTED_RESULTS_FILE_KEYS = ["name", "filters", "expected_results_last_updated", "expected_results"]


class E2ETestResultsHandler:
    """
    Handles generating and comparing actual and expected results for end-to-end testing of various
    RuFaS modules.
    """

    @staticmethod
    def compare_actual_and_expected_test_results(json_output_path: Path) -> None:
        """
        Orchestrates the comparison between the expected and actual end-to-end testing results.

        Parameters
        ----------
        json_output_directory : Path
            Path to which JSON outputs are written to.

        """
        om = OutputManager()
        info_map: dict[str, Any] = {
            "class": E2ETestResultsHandler.__class__.__name__,
            "function": E2ETestResultsHandler.compare_actual_and_expected_test_results.__name__,
        }
        test_result_path_sets = E2ETestResultsHandler._get_test_result_paths()

        for path_set in test_result_path_sets:
            info_map["domain"] = path_set.domain
            om.add_log(
                f"End-to-end testing for {path_set.domain}",
                "Collecting and comparing actual and expected results",
                info_map,
            )
            matching_path = E2ETestResultsHandler._get_matching_path(json_output_path, path_set)
            if matching_path:
                path_to_actual_results = matching_path
            else:
                om.add_error(
                    f"End-to-end testing failed for {path_set.domain}.",
                    "Could not find actual end-to-end testing results",
                    info_map,
                )
                continue
            with open(path_to_actual_results, "r") as results:
                actual_results = json.load(results)
            with open(f"{path_set.expected_results_path}", "r") as e_to_e_results:
                filter_and_results = json.load(e_to_e_results)
                expected_results = filter_and_results["expected_results"]

            diff = DeepDiff(expected_results, actual_results, ignore_order=True, verbose_level=2, significant_digits=3)

            filtered_diff = E2ETestResultsHandler.filter_insignificant_changes(diff, path_set.tolerance)

            is_difference_in_results: bool = False if (filtered_diff == {}) else True
            if is_difference_in_results:
                om.add_error(
                    f"End-to-end testing failed for {path_set.domain}",
                    "Identified differences between actual and expected results.",
                    info_map,
                )
            else:
                om.add_log(
                    f"End-to-end testing succeeded for {path_set.domain}",
                    "No differences found between actual and expected end-to-end testing results.",
                    info_map,
                )
            end_to_end_testing_passing: bool = not is_difference_in_results
            filtered_diff.update({"end_to_end_testing_passing": end_to_end_testing_passing})
            info_map.update({"units": MeasurementUnits.UNITLESS, "prefix": path_set.domain})
            for comparison_type, difference in filtered_diff.items():
                om.add_variable(comparison_type, difference, info_map)

    @staticmethod
    def _get_test_result_paths() -> list[ResultPathType]:
        """Retrieves the paths to test results and associated information from the InputManager."""
        im = InputManager()
        result_paths: list[dict[str, str]] = im.get_data("end_to_end_testing_result_paths.end_to_end_test_result_paths")
        test_result_paths: list[ResultPathType] = []
        for path_set in result_paths:
            test_result_paths.append(
                ResultPathType(
                    path_set["domain"],
                    path_set["expected_results_path"],
                    path_set["actual_results_path"],
                    path_set["tolerance"],
                )
            )
        return test_result_paths

    @staticmethod
    def is_significant(changes: dict[str, float | str], tolerance: float) -> bool:
        """
        Determines if a numerical change is significant based if the change between the
        "old_value" and "new_value" exceeds the specified tolerance.

        Parameters
        ----------
        changes : dict[str, float | str]
            A dictionary representing changes with "old_value" and "new_value".
        tolerance : float
            The threshold for considering a difference as significant.

        Returns
        -------
        bool
            True if the change is both numerical and significant, False otherwise.

        Notes
        -----
        The comparison is based on the absolute difference between the "old_value" and "new_value",
        relative to the "old_value". If the "old_value" is zero, a fallback reference value of 1 is used
        to ensure the tolerance comparison remains meaningful.
        """
        if isinstance(changes, dict) and "old_value" in changes and "new_value" in changes:
            old_value = changes["old_value"]
            new_value = changes["new_value"]
            if isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)):
                reference = abs(old_value) if abs(old_value) > 0 else 1
                difference = abs(new_value - old_value)
                return difference > tolerance * GeneralConstants.PERCENTAGE_TO_FRACTION * reference
        return True

    @staticmethod
    def filter_nested(values_changed: dict[str, dict[str, float | str]], tolerance: float) -> None:
        """
        Recursively filters out insignificant numerical changes from a nested structure.

        Parameters
        ----------
        values_changed : dict[str, dict[str, float | str]]
            The `values_changed` section of a DeepDiff result.
        tolerance : float
            The threshold for considering a difference as significant.

        Notes
        -----
        This method modifies `values_changed` in place.
        """
        keys_to_remove = []
        for key, change in values_changed.items():
            if isinstance(change, dict) and "old_value" not in change and "new_value" not in change:
                E2ETestResultsHandler.filter_nested(change, tolerance)
                if not change:
                    keys_to_remove.append(key)
            elif not E2ETestResultsHandler.is_significant(change, tolerance):
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del values_changed[key]

    @staticmethod
    def filter_insignificant_changes(
        diff_result: dict[str, dict[str, dict[str, float | str]]], tolerance: float
    ) -> dict[str, dict[str, dict[str, float | str]]]:
        """
        Removes insignificant changes from a DeepDiff `values_changed` section.

        Parameters
        ----------
        diff_result : dict[str, dict[str, dict[str, float | str]]]
            The DeepDiff result to filter.
        tolerance : float
            The threshold for considering a difference as significant.

        Returns
        -------
        dict[str, dict[str, dict[str, float | str]]]
            The filtered DeepDiff result.
        """
        values_changed = diff_result.get("values_changed", {})
        E2ETestResultsHandler.filter_nested(values_changed, tolerance)
        return diff_result

    @staticmethod
    def update_expected_test_results(output_dir: Path) -> None:
        """
        Compares the actual end-to-end testing results for various RuFaS domains and updates the expected
        results in the appropriate domain filter file if differences are found.

        Parameters
        ----------
        output_dir : str
            The directory to which the actual results are written to.
        """
        om = OutputManager()
        info_map: dict[str, Any] = {
            "class": E2ETestResultsHandler.__class__.__name__,
            "function": E2ETestResultsHandler.update_expected_test_results.__name__,
        }
        test_result_path_sets = E2ETestResultsHandler._get_test_result_paths()
        for path_set in test_result_path_sets:
            info_map["domain"] = path_set.domain
            om.add_log(
                f"End-to-end testing for {path_set.domain}",
                "Generating fresh results.",
                info_map,
            )

            matching_path = E2ETestResultsHandler._get_matching_path(output_dir, path_set)
            if matching_path:
                path_to_actual_results = matching_path
            else:
                om.add_error(
                    "End-to-end testing expected results update failure.",
                    f"Could not find actual end-to-end testing results for {path_set.domain} domain.",
                    info_map,
                )
                continue
            backup_path = Path(f"{path_set.expected_results_path}.bak")
            shutil.copy(path_set.expected_results_path, backup_path)
            try:
                with open(path_to_actual_results, "r") as actual_results_file:
                    actual_results = json.load(actual_results_file)

                expected_results_path = Path(path_set.expected_results_path)
                with open(expected_results_path, "r") as expected_results_file:
                    expected_results = json.load(expected_results_file)

                diff = DeepDiff(
                    expected_results["expected_results"], actual_results, ignore_order=True, verbose_level=2
                )
                is_difference_in_results: bool = False if (diff == {}) else True
                if is_difference_in_results:
                    om.add_warning(
                        "End-to-end testing expected results different from new actual results",
                        f"Differences will be saved in {output_dir} for {path_set.domain} domain.",
                        info_map,
                    )
                    save_path = output_dir / f"{path_set.domain}_update_diff.json"
                    om.dict_to_file_json(data_dict=diff, path=save_path)
                else:
                    om.add_log(
                        "End-to-end testing expected results matched new actual results",
                        f"No differences detected in actual and expected results for {path_set.domain} domain.",
                        info_map,
                    )
                minified_actual_results = Utility.make_serializable(
                    actual_results, max_depth=om.JSON_OUTPUT_MAX_RECURSIVE_DEPTH
                )
                expected_results["expected_results"] = minified_actual_results
                expected_results["expected_results_last_updated"] = Utility.get_timestamp(include_millis=False)
                E2ETestResultsHandler._write_formatted_json(expected_results_path, expected_results)
            except (IOError, json.JSONDecodeError) as e:
                om.add_error(
                    "End-to-end testing expected results update failure.",
                    f"Failed to update expected results for {path_set.domain} domain. Error: {str(e)}."
                    " Restoring backup.",
                    info_map,
                )
                shutil.move(backup_path, path_set.expected_results_path)
                raise e
            finally:
                if backup_path.exists():
                    backup_path.unlink()

    @staticmethod
    def _get_matching_path(dir_path: Path, path_set: ResultPathType) -> Path | None:
        """
        Returns the path that matches the path_set actual results path.

        Parameters
        ----------
        dir_path : Path
            The path to the directory.
        path_set : ResultPathType
            ResultPathType object containing the domain, expected results path, actual results path, and tolerance.

        Returns
        -------
        Path
            The matching path.
        """
        path_to_actual_results = None
        for path in dir_path.iterdir():
            actual_results_base_path = Path(path_set.actual_results_path)
            is_a_match = path.name.startswith(actual_results_base_path.name)
            if is_a_match:
                path_to_actual_results = path
                break
        return path_to_actual_results

    @staticmethod
    def _write_formatted_json(file_path: Path, data: dict[str, str]) -> None:
        """
        Writes a JSON file with custom serialization settings for the "expected_results" field.

        Parameters
        ----------
        file_path : Path
            The path to the JSON file.
        data : dict
            The data to write to the JSON file.
        """
        key_order = ORDERED_EXPECTED_RESULTS_FILE_KEYS
        missing_keys = [key for key in key_order if key not in data]
        if missing_keys:
            om = OutputManager()
            om.add_error(
                "End-to-end testing expected results update failure.",
                f"Expected results file missing required keys in data: {missing_keys}",
                {
                    "class": E2ETestResultsHandler.__class__.__name__,
                    "function": E2ETestResultsHandler._write_formatted_json.__name__,
                },
            )
            raise ValueError(f"Missing required keys in data: {missing_keys}")

        ordered_data = {key: data[key] for key in key_order}
        compact_expected_results = json.dumps(ordered_data["expected_results"], separators=(",", ":"))
        ordered_data["expected_results"] = "__EXPECTED_RESULTS_PLACEHOLDER__"

        json_string = json.dumps(ordered_data, indent=4)
        json_string = json_string.replace('"__EXPECTED_RESULTS_PLACEHOLDER__"', compact_expected_results)
        invalid_prefix = "// WARNING: This is an autogenerated file. Remove this line for valid JSON.\n"
        json_string = invalid_prefix + json_string
        with open(file_path, "w") as file:
            file.write(json_string)

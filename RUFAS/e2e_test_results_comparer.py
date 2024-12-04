import json
from collections import namedtuple
from pathlib import Path
from typing import Any

from deepdiff import DeepDiff

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.units import MeasurementUnits

ResultPathType = namedtuple("ResultPathType", ["domain", "expected_results_path", "actual_results_path", "tolerance"])


class E2ETestResultsComparer:
    """
    Contains routines to handle comparing actual and expected results for end-to-end testing of various RuFaS modules.
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
            "class": E2ETestResultsComparer.__class__.__name__,
            "function": E2ETestResultsComparer.compare_actual_and_expected_test_results.__name__,
        }
        test_result_path_sets = E2ETestResultsComparer._get_test_result_paths()

        for path_set in test_result_path_sets:
            info_map["domain"] = path_set.domain
            om.add_log(
                f"End-to-end testing for {path_set.domain}",
                "Collecting and comparing actual and expected results",
                info_map,
            )
            path_to_actual_results = None
            for path in json_output_path.iterdir():
                actual_results_base_path = Path(path_set.actual_results_path)
                is_a_match = path.name.startswith(actual_results_base_path.name)
                if is_a_match:
                    path_to_actual_results = path
                    break
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

            diff = DeepDiff(expected_results, actual_results, ignore_order=True, verbose_level=2, significant_digits=6)

            filtered_diff = E2ETestResultsComparer.filter_insignificant_changes(diff, path_set.tolerance)

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
                ResultPathType(path_set["domain"], path_set["expected_results_path"], path_set["actual_results_path"],
                               path_set["tolerance"])
            )
        return test_result_paths

    @staticmethod
    def is_significant(change: dict[str, float | str], tolerance: float) -> bool:
        """
        Determines if a numerical change is significant based on the symmetric relative tolerance.

        Parameters
        ----------
        change : dict[str, float | str]
            A dictionary representing a change with "old_value" and "new_value".
        tolerance : float
            The threshold for considering a difference as significant.

        Returns
        -------
        bool
            True if the change is both numerical and significant, False otherwise.
        """
        if isinstance(change, dict) and "old_value" in change and "new_value" in change:
            old_value = change["old_value"]
            new_value = change["new_value"]
            if isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)):
                reference = (abs(new_value) + abs(old_value)) / 2
                if reference == 0:
                    return False
                difference = abs(new_value - old_value)
                return difference > tolerance * reference
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
                E2ETestResultsComparer.filter_nested(change, tolerance)
                if not change:
                    keys_to_remove.append(key)
            elif not E2ETestResultsComparer.is_significant(change, tolerance):
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
        E2ETestResultsComparer.filter_nested(values_changed, tolerance)
        return diff_result

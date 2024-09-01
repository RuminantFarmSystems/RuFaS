from collections import namedtuple
from deepdiff import DeepDiff
from pathlib import Path
from typing import Any

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.units import MeasurementUnits

import json
import re


TestResultPathType = namedtuple("TestResultPaths", ["domain", "expected_results_path", "actual_results_path"])


class EndToEndTestResultsComparer:
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
            "class": EndToEndTestResultsComparer.__class__.__name__,
            "function": EndToEndTestResultsComparer.compare_actual_and_expected_test_results.__name__,
        }
        test_result_path_sets = EndToEndTestResultsComparer._get_test_result_paths()
        for path_set in test_result_path_sets:
            om.add_log(
                f"End-to-end testing for {path_set.domain}",
                "Collecting and comparing actual and expected results",
                info_map,
            )
            path_to_actual_results = None
            for path in json_output_path.iterdir():
                is_a_match = re.match(f"{str(json_output_path)}/{path_set.actual_results_path}.*", str(path))
                if is_a_match:
                    path_to_actual_results = path
                    break
            else:
                om.add_error(
                    f"Could not find actual end-to-end testing results for {path_set.domain}",
                    "End-to-end testing failed.",
                    info_map,
                )
                continue
            with open(path_to_actual_results, "r") as results:
                actual_results = json.load(results)
            with open(f"{path_set.expected_results_path}", "r") as e_to_e_results:
                filter_and_results = json.load(e_to_e_results)
                expected_results = filter_and_results["expected_results"]

            diff = DeepDiff(expected_results, actual_results, ignore_order=True, verbose_level=2)

            is_difference_in_results = diff == {}
            if is_difference_in_results:
                om.add_log(
                    f"End-to-end testing succeeded for {path_set.domain}",
                    "No differences found between actual and expected end-to-end testing results.",
                    info_map,
                )
            else:
                om.add_error(
                    f"Failed end-to-end testing for {path_set.domain}",
                    "Identified differences between actual and expected results.",
                    info_map,
                )
            diff.update({"end_to_end_testing_passing": is_difference_in_results})
            info_map.update({"units": MeasurementUnits.UNITLESS, "prefix": path_set.domain})
            for comparison_type, difference in diff.items():
                om.add_variable(comparison_type, difference, info_map)

    @staticmethod
    def _get_test_result_paths() -> list[TestResultPathType]:
        """Retrieves the paths to test results and associated information from the InputManager."""
        im = InputManager()
        result_paths: list[dict[str, str]] = im.get_data("end_to_end_testing_result_paths.end_to_end_test_result_paths")
        test_result_paths: list[TestResultPathType] = []
        for path_set in result_paths:
            test_result_paths.append(
                TestResultPathType(
                    path_set["domain"], path_set["expected_results_path"], path_set["actual_results_path"]
                )
            )
        return test_result_paths

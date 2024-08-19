from collections import namedtuple
from deepdiff import DeepDiff
from pathlib import Path

from RUFAS.output_manager import OutputManager
from RUFAS.units import MeasurementUnits

import json
import re


ResultsCollection = namedtuple("ResultsCollection", ["output_prefix", "expected_results_path", "actual_results_path"])


RESULTS_TO_COMPARE = [ResultsCollection("FeedStorageResults", "e2e_json_feed_storage_filter", "e2e_vars")]


class EndToEndTester:
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
        info_map = {
            "class": EndToEndTester.__class__.__name__,
            "function": EndToEndTester.compare_actual_and_expected_test_results.__name__,
        }
        for result_set in RESULTS_TO_COMPARE:
            path_to_actual_results = None
            for path in json_output_path.iterdir():
                is_a_match = re.match(
                    f"{str(json_output_path)}/end-to-end-testing_saved_variables_{result_set.actual_results_path}_.*",
                    str(path),
                )
                if is_a_match:
                    path_to_actual_results = path
                    break
            else:
                om.add_error(
                    "Could not find actual end-to-end testing results.", "End-to-end testing failed.", info_map
                )
                return
            with open(path_to_actual_results, "r") as results:
                actual_results = json.load(results)
            with open(f"input/data/end_to_end_testing/{result_set.expected_results_path}.json", "r") as e_to_e_results:
                filter_and_results = json.load(e_to_e_results)
                expected_results = filter_and_results["expected_results"]

            diff = DeepDiff(expected_results, actual_results, ignore_order=True, verbose_level=2)

            is_difference_in_results = diff == {}
            if is_difference_in_results:
                om.add_log(
                    "End-to-end testing succeeded",
                    "No differences found between actual and expected end-to-end testing results.",
                    info_map,
                )
            else:
                om.add_error(
                    "Failed end-to-end testing", "Identified differences between actual and expected results.", info_map
                )
            diff.update({"end_to_end_testing_passing": is_difference_in_results})
            info_map.update({"units": MeasurementUnits.UNITLESS, "prefix": result_set.output_prefix})
            for comparison_type, difference in diff.items():
                om.add_variable(comparison_type, difference, info_map)

from collections import namedtuple
from deepdiff import DeepDiff
from pathlib import Path
from typing import Any

from RUFAS.output_manager import OutputManager
from RUFAS.units import MeasurementUnits

import json
import re


TestResultPaths = namedtuple("TestResultPaths", ["domain_prefix", "expected_results_path", "actual_results_path"])


"""
Maps a RuFaS domain that is supported for end-to-end testing to information needed to collect actual and expected
results for testing that domain, and the prefix used when saving the test results to the Output Manager.
"""
DOMAINS = {
    "Feed Storage": TestResultPaths(
        "FeedStorageResults",
        "end-to-end-testing_saved_variables_e2e_json_feed_storage_filter",
        "input/data/end_to_end_testing/e2e_feed_storage.json",
    )
}


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
        info_map: dict[str, Any] = {
            "class": EndToEndTester.__class__.__name__,
            "function": EndToEndTester.compare_actual_and_expected_test_results.__name__,
        }
        for domain, info in DOMAINS.items():
            om.add_log(
                f"End-to-end testing for {domain}", "Collecting and comparing actual and expected results", info_map
            )
            path_to_actual_results = None
            for path in json_output_path.iterdir():
                is_a_match = re.match(f"{str(json_output_path)}/{info.actual_results_path}.*", str(path))
                if is_a_match:
                    path_to_actual_results = path
                    break
            else:
                om.add_error(
                    f"Could not find actual end-to-end testing results for {domain}",
                    "End-to-end testing failed.",
                    info_map
                )
                return
            with open(path_to_actual_results, "r") as results:
                actual_results = json.load(results)
            with open(f"{info.expected_results_path}", "r") as e_to_e_results:
                filter_and_results = json.load(e_to_e_results)
                expected_results = filter_and_results["expected_results"]

            diff = DeepDiff(expected_results, actual_results, ignore_order=True, verbose_level=2)

            is_difference_in_results = diff == {}
            if is_difference_in_results:
                om.add_log(
                    f"End-to-end testing succeeded for {domain}",
                    "No differences found between actual and expected end-to-end testing results.",
                    info_map,
                )
            else:
                om.add_error(
                    f"Failed end-to-end testing for {domain}",
                    "Identified differences between actual and expected results.",
                    info_map
                )
            diff.update({"end_to_end_testing_passing": is_difference_in_results})
            info_map.update({"units": MeasurementUnits.UNITLESS, "prefix": info.domain_prefix})
            for comparison_type, difference in diff.items():
                om.add_variable(comparison_type, difference, info_map)

import json
import re
from collections import namedtuple
import math
from numbers import Number
from collections.abc import Iterable
from pathlib import Path
import shutil
from typing import Any

import pandas as pd
from deepdiff import DeepDiff

from RUFAS.data_validator import DataValidator
from RUFAS.general_constants import GeneralConstants
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.units import MeasurementUnits
from RUFAS.util import Utility

TOLERANCE_TYPE_PERCENT = "percent"
TOLERANCE_TYPE_ABSOLUTE = "absolute"
TOLERANCE_TYPE_SIGNIFICANT_DIGITS = "significant_digits"
TOLERANCE_TYPES = (TOLERANCE_TYPE_PERCENT, TOLERANCE_TYPE_ABSOLUTE, TOLERANCE_TYPE_SIGNIFICANT_DIGITS)
ResultPathType = namedtuple(
    "ResultPathType",
    [
        "domain",
        "expected_results_path",
        "actual_results_path",
        "tolerance",
        "must_change_variables_path",
        "accepted_ranges_path",
        "tolerance_type",
        "variable_tolerances_path",
    ],
    defaults=["", "", TOLERANCE_TYPE_PERCENT, ""],
)
ORDERED_EXPECTED_RESULTS_FILE_KEYS = ["name", "filters", "expected_results_last_updated", "expected_results"]
MUST_CHANGE_VARIABLES_KEY = "must_change_variables"
ACCEPTED_RANGES_KEY = "accepted_ranges"
ACCEPTED_RANGE_MIN_KEY = "min"
ACCEPTED_RANGE_MAX_KEY = "max"
VARIABLE_TOLERANCES_KEY = "variable_tolerances"
TOLERANCE_KEY = "tolerance"
TOLERANCE_TYPE_KEY = "tolerance_type"
TOLERANCE_REQUIREMENTS = (
    f"'{TOLERANCE_TYPE_KEY}' must be one of {list(TOLERANCE_TYPES)}, a '{TOLERANCE_TYPE_PERCENT}' or "
    f"'{TOLERANCE_TYPE_ABSOLUTE}' '{TOLERANCE_KEY}' must be a number of at least 0, and a "
    f"'{TOLERANCE_TYPE_SIGNIFICANT_DIGITS}' '{TOLERANCE_KEY}' must be a whole number of at least 1"
)
TOP_LEVEL_DIFF_PATH_PATTERN = re.compile(r"""^root\[(?:'([^']+)'|"([^"]+)")\]""")


class E2ETestResultsHandler:
    """Handles generating and comparing actual and expected results for end-to-end testing of various RuFaS modules."""

    @staticmethod
    def compare_actual_and_expected_test_results(
        json_output_path: Path,
        convert_variable_table_path: str | None,
        output_prefix: str,
        must_change_variables: set[str],
        accepted_ranges: dict[str, dict[str, Any]],
        variable_tolerances: dict[str, dict[str, Any]],
    ) -> None:
        """
        Orchestrates the comparison between the expected and actual end-to-end testing results.

        Parameters
        ----------
        json_output_path : Path
            Path to which JSON outputs are written to.
        convert_variable_table_path : str | None
            String path to the csv lookup table to convert the variable names in the expected results to match the
            variable names in the actual results.
        output_prefix : str
            The output prefix for the current e2e run.
        must_change_variables : set[str]
            The names of the variables flagged as must-change, as returned by ``validate_comparison_configuration``.
        accepted_ranges : dict[str, dict[str, Any]]
            The accepted ranges of the input set's variables, keyed by variable name, as returned by
            ``validate_comparison_configuration``. Empty when accepted ranges are not used.
        variable_tolerances : dict[str, dict[str, Any]]
            The tolerance overrides of the input set's variables, keyed by variable name, as returned by
            ``validate_comparison_configuration``.

        Notes
        -----
        Each domain's values are compared with the domain's ``tolerance``, interpreted according to its
        ``tolerance_type`` (see ``_exceeds_tolerance``). A variable listed in the input set's variable tolerances
        file is compared with its own tolerance and tolerance type instead, for the regular comparison and for the
        must-change check alike.

        Variables flagged in the input set's must-change variables file are held to the opposite assertion of the
        regular comparison: each flagged variable must differ from its recorded expected value beyond the domain
        tolerance, and its differences are not reported as regular failures. The comparison results additionally
        report ``changed_variables``, the names of the unflagged variables whose values differ from the expected
        results, so a subject matter expert can evaluate them and flag the ones that are expected to change.

        The variables with an accepted range are likewise left out of the regular comparison and are graded against
        their accepted range instead: every numerical value of such a variable must fall within the range, whether or
        not it differs from the recorded expected value. The comparison results report each range together with the
        observed extremes of its variable.
        """
        om = OutputManager()
        info_map: dict[str, Any] = {
            "class": E2ETestResultsHandler.__name__,
            "function": E2ETestResultsHandler.compare_actual_and_expected_test_results.__name__,
        }
        test_result_path_sets = E2ETestResultsHandler._get_test_result_paths(output_prefix)

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
            with open(path_to_actual_results, "r", encoding="utf-8") as results:
                actual_results = json.load(results)
            expected_results = E2ETestResultsHandler._load_expected_results_file(path_set, convert_variable_table_path)[
                "expected_results"
            ]

            domain_must_change_variables = sorted(name for name in must_change_variables if name in expected_results)
            domain_accepted_ranges = {
                name: accepted_ranges[name] for name in sorted(accepted_ranges) if name in expected_results
            }
            domain_variable_tolerances = {
                name: variable_tolerances[name] for name in sorted(variable_tolerances) if name in expected_results
            }
            excluded_variables = must_change_variables | set(accepted_ranges)
            comparison_expected_not_excluded = {
                k: v for k, v in expected_results.items() if k not in excluded_variables
            }
            comparison_actual_not_excluded = {k: v for k, v in actual_results.items() if k not in excluded_variables}

            diff = DeepDiff(
                comparison_expected_not_excluded,
                comparison_actual_not_excluded,
                ignore_order=True,
                verbose_level=2,
                significant_digits=3,
            )

            filtered_diff = E2ETestResultsHandler.filter_insignificant_changes(
                diff, path_set.tolerance, path_set.tolerance_type, domain_variable_tolerances
            )
            must_change_satisfied, must_change_violations = E2ETestResultsHandler._evaluate_must_change_variables(
                expected_results,
                actual_results,
                domain_must_change_variables,
                path_set.tolerance,
                path_set.tolerance_type,
                domain_variable_tolerances,
            )
            accepted_range_satisfied, accepted_range_violations = E2ETestResultsHandler._evaluate_accepted_ranges(
                actual_results, domain_accepted_ranges
            )
            E2ETestResultsHandler._report_domain_comparison_results(
                domain=path_set.domain,
                filtered_diff=filtered_diff,
                domain_must_change_variables=domain_must_change_variables,
                must_change_satisfied=must_change_satisfied,
                must_change_violations=must_change_violations,
                accepted_range_satisfied=accepted_range_satisfied,
                accepted_range_violations=accepted_range_violations,
                info_map=info_map,
            )

    @staticmethod
    def validate_comparison_configuration(
        output_prefix: str,
        convert_variable_table_path: str | None,
        filters_directory: Path,
        use_accepted_ranges: bool,
    ) -> tuple[set[str], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
        """
        Validates the comparison configuration of an end-to-end testing input set before the simulation runs.

        Parameters
        ----------
        output_prefix : str
            The output prefix of the end-to-end testing input set.
        convert_variable_table_path : str | None
            String path to the csv lookup table to convert the variable names in the expected results to match the
            variable names in the actual results.
        filters_directory : Path
            The directory the task loads its filter files from.
        use_accepted_ranges : bool
            Whether the input set's accepted ranges files are loaded, so that the comparison grades the listed
            variables against their accepted range instead of the recorded expected results. When ``False``, the
            files are not read.

        Returns
        -------
        tuple[set[str], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]
            The names of the variables flagged as must change, the accepted ranges keyed by variable name (empty
            when ``use_accepted_ranges`` is ``False``), and the tolerance overrides keyed by variable name, for
            ``compare_actual_and_expected_test_results``.

        Raises
        ------
        ValueError
            If the configuration is not valid. The message lists every problem found: must-change variables files,
            accepted ranges files, variable tolerances files, expected results files, or a conversion table that
            cannot be loaded, result path sets that cannot be resolved once the simulation has run or whose domain
            tolerance is not valid (see ``_validate_result_path_set``), and must-change variables, variables with an
            accepted range, or variables with a tolerance override that are not found in the expected results of
            any domain.

        Notes
        -----
        Runs the checks of ``compare_actual_and_expected_test_results`` that do not depend on the actual results:
        the input set's must-change variables files, accepted ranges files, variable tolerances files, expected
        results files, and conversion table must load, every result path set must resolve to actual results the run
        will write and carry a valid domain tolerance, and every must-change variable, every variable with an
        accepted range, and every variable with a tolerance override must be a key of at least one domain's
        expected results. Running these checks before the simulation makes a configuration mistake, such as a
        mistyped path or variable name, fail the task in seconds instead of after the full simulation. The
        comparison does not repeat them, so it relies on this validation having passed.

        Every check runs before the error is raised, so one run reports all the problems of the input set. The
        must-change, ranged, and overridden variable names are only checked when every expected results file could
        be loaded, because a name may belong to a file that could not be read.
        """
        info_map: dict[str, Any] = {
            "class": E2ETestResultsHandler.__name__,
            "function": E2ETestResultsHandler.validate_comparison_configuration.__name__,
        }
        errors: list[str] = []
        test_result_path_sets = E2ETestResultsHandler._get_test_result_paths(output_prefix)

        must_change_variables: set[str] = set()
        checked_must_change_paths: set[str] = set()
        for path_set in test_result_path_sets:
            if path_set.must_change_variables_path in checked_must_change_paths:
                continue
            checked_must_change_paths.add(path_set.must_change_variables_path)
            try:
                must_change_variables.update(E2ETestResultsHandler._load_must_change_variables([path_set]))
            except (FileNotFoundError, ValueError) as e:
                E2ETestResultsHandler._record_configuration_error(errors, str(e))

        accepted_ranges: dict[str, dict[str, Any]] = (
            E2ETestResultsHandler._collect_accepted_ranges(test_result_path_sets, errors) if use_accepted_ranges else {}
        )
        variable_tolerances = E2ETestResultsHandler._collect_variable_tolerances(test_result_path_sets, errors)

        matched_must_change_variables: set[str] = set()
        matched_ranged_variables: set[str] = set()
        matched_overridden_variables: set[str] = set()
        all_expected_results_loaded = True
        for path_set in test_result_path_sets:
            file_content = E2ETestResultsHandler._validate_result_path_set(
                path_set, output_prefix, filters_directory, errors, convert_variable_table_path
            )
            if file_content is None:
                all_expected_results_loaded = False
                continue
            expected_results = file_content["expected_results"]
            matched_must_change_variables.update(name for name in must_change_variables if name in expected_results)
            matched_ranged_variables.update(name for name in accepted_ranges if name in expected_results)
            matched_overridden_variables.update(name for name in variable_tolerances if name in expected_results)

        if all_expected_results_loaded:
            E2ETestResultsHandler._record_unknown_variables(
                errors,
                "End-to-end testing must-change configuration error",
                "Must-change variables",
                must_change_variables - matched_must_change_variables,
                info_map,
            )
            E2ETestResultsHandler._record_unknown_variables(
                errors,
                "End-to-end testing accepted-range configuration error",
                "Variables with an accepted range",
                set(accepted_ranges) - matched_ranged_variables,
                info_map,
            )
            E2ETestResultsHandler._record_unknown_variables(
                errors,
                "End-to-end testing tolerance configuration error",
                "Variables with a tolerance override",
                set(variable_tolerances) - matched_overridden_variables,
                info_map,
            )
        if errors:
            E2ETestResultsHandler._raise_configuration_errors(errors)
        return must_change_variables, accepted_ranges, variable_tolerances

    @staticmethod
    def validate_update_configuration(output_prefix: str, filters_directory: Path) -> None:
        """
        Validates the expected results update configuration of an input set before the simulation runs.

        Parameters
        ----------
        output_prefix : str
            The output prefix of the end-to-end testing input set.
        filters_directory : Path
            The directory the task loads its filter files from.

        Raises
        ------
        ValueError
            If the configuration is not valid. The message lists every problem found: expected results files that
            cannot be loaded or are missing a required key, and result path sets that cannot be resolved once the
            simulation has run (see ``_validate_result_path_set``).

        Notes
        -----
        Runs the checks of ``update_expected_test_results`` that do not depend on the actual results, so that a
        mistyped path or an incomplete expected results file fails the task in seconds instead of after the full
        simulation. The must-change variables files are not checked because the update does not read them. Every
        check runs before the error is raised, so one run reports all the problems of the input set.
        """
        errors: list[str] = []
        for path_set in E2ETestResultsHandler._get_test_result_paths(output_prefix):
            file_content = E2ETestResultsHandler._validate_result_path_set(
                path_set, output_prefix, filters_directory, errors
            )
            if file_content is None:
                continue
            try:
                E2ETestResultsHandler._check_expected_results_file_keys(file_content)
            except ValueError as e:
                E2ETestResultsHandler._record_configuration_error(
                    errors,
                    f"Expected results file {path_set.expected_results_path} for {path_set.domain}: "
                    + str(e).removeprefix("E2E testing error: "),
                )
        if errors:
            E2ETestResultsHandler._raise_configuration_errors(errors)

    @staticmethod
    def _report_domain_comparison_results(
        domain: str,
        filtered_diff: dict[str, Any],
        domain_must_change_variables: list[str],
        must_change_satisfied: list[str],
        must_change_violations: dict[str, str],
        accepted_range_satisfied: dict[str, dict[str, Any]],
        accepted_range_violations: dict[str, dict[str, Any]],
        info_map: dict[str, Any],
    ) -> None:
        """
        Logs the outcome of a domain's end-to-end comparison and records the comparison results as variables.

        Parameters
        ----------
        domain : str
            The RuFaS domain the comparison results belong to.
        filtered_diff : dict[str, Any]
            The domain's ``DeepDiff`` result with insignificant changes filtered out.
        domain_must_change_variables : list[str]
            The must-change variable names present in the domain's expected results.
        must_change_satisfied : list[str]
            The must-change variables whose values differ from the expected results.
        must_change_violations : dict[str, str]
            The violating must-change variables, mapped to the reason each one failed.
        accepted_range_satisfied : dict[str, dict[str, Any]]
            The variables whose values all fall within their accepted range, mapped to the range and the observed
            extremes.
        accepted_range_violations : dict[str, dict[str, Any]]
            The variables violating their accepted range, mapped to the range, the observed extremes when available,
            and the reason each one failed.
        info_map : dict[str, Any]
            Information about the source of the recorded variables. Updated in place with the units and the
            ``domain`` output prefix.

        Notes
        -----
        The domain passes when the filtered diff is empty and there are no must-change or accepted-range violations;
        each failure cause is logged as an error, and the recorded results include ``changed_variables`` (the names
        of the unflagged variables that differ), the must-change outcomes, and the accepted-range outcomes.
        """
        om = OutputManager()
        changed_variables = E2ETestResultsHandler._extract_changed_variable_names(filtered_diff)
        is_difference_in_results: bool = False if (filtered_diff == {}) else True
        if is_difference_in_results:
            om.add_error(
                f"End-to-end testing failed for {domain}",
                "Identified differences between actual and expected results.",
                info_map,
            )
        if must_change_violations:
            om.add_error(
                f"End-to-end testing failed for {domain}",
                f"Must-change variables did not change: {sorted(must_change_violations)}",
                info_map,
            )
        if accepted_range_violations:
            om.add_error(
                f"End-to-end testing failed for {domain}",
                f"Variables violating their accepted range: {sorted(accepted_range_violations)}",
                info_map,
            )
        end_to_end_testing_passing: bool = (
            not is_difference_in_results and not must_change_violations and not accepted_range_violations
        )
        if end_to_end_testing_passing:
            om.add_log(
                f"End-to-end testing succeeded for {domain}",
                "No differences found between actual and expected end-to-end testing results.",
                info_map,
            )
        comparison_results: dict[str, Any] = dict(filtered_diff)
        if changed_variables:
            comparison_results["changed_variables"] = changed_variables
        if domain_must_change_variables:
            comparison_results["must_change_satisfied"] = must_change_satisfied
            comparison_results["must_change_violations"] = must_change_violations
        if accepted_range_satisfied or accepted_range_violations:
            comparison_results["accepted_range_satisfied"] = accepted_range_satisfied
            comparison_results["accepted_range_violations"] = accepted_range_violations
        comparison_results["end_to_end_testing_passing"] = end_to_end_testing_passing
        info_map.update({"units": MeasurementUnits.UNITLESS, "prefix": domain})
        for comparison_type, difference in comparison_results.items():
            om.add_variable(comparison_type, difference, info_map)

    @staticmethod
    def process_test_result_averaging(
        e2e_group: str,
        e2e_runs: list[dict[str, Any]],
    ) -> Path:
        """
        Processes the averaging of end-to-end test results across multiple runs in the same E2E test group.

        Creates a directory for the averaged results, identifies each set of E2E result files to average, averages the
        corresponding results across the provided runs, and writes each set of averaged results to a JSON file.

        Parameters
        ----------
        e2e_group : str
            The name of the E2E test group whose results are being averaged.
        e2e_runs : list[dict[str, Any]]
            The E2E run configurations belonging to the test group. Each run must contain the information needed to
            locate its generated result files.

        Returns
        -------
        Path
            The directory containing the averaged E2E result files.

        Raises
        ------
        ValueError
            If no E2E runs are provided or if the result files for a run cannot be uniquely identified.
        """
        if not e2e_runs:
            OutputManager().add_error(
                "E2E Results Averaging Error",
                "No E2E runs data sent to 'process_test_result_averaging()' function.",
                info_map={
                    "class": E2ETestResultsHandler.__class__.__name__,
                    "function": E2ETestResultsHandler.process_test_result_averaging.__name__,
                },
            )
            raise ValueError(f"Cannot average E2E results for '{e2e_group}' because no runs were provided.")

        json_output_directory = Path(e2e_runs[0]["json_output_directory"])

        averaged_results_directory = json_output_directory / "averaged" / e2e_group
        OutputManager().create_directory(averaged_results_directory)

        test_result_path_sets = E2ETestResultsHandler._get_test_result_paths(e2e_group)

        for path_set in test_result_path_sets:
            result_paths = E2ETestResultsHandler._extract_results_paths(
                e2e_runs=e2e_runs,
                json_output_directory=json_output_directory,
                actual_results_path=Path(path_set.actual_results_path),
            )

            averaged_results = E2ETestResultsHandler._average_test_results(
                result_paths,
            )

            averaged_result_path = (
                averaged_results_directory / f"{Path(path_set.actual_results_path).name}_averaged.json"
            )

            with open(
                averaged_result_path,
                "w",
                encoding="utf-8",
            ) as averaged_file:
                json.dump(
                    averaged_results,
                    averaged_file,
                    separators=(",", ":"),
                )

        return averaged_results_directory

    @staticmethod
    def _average_test_results(
        results_paths: list[Path],
    ) -> dict[str, Any]:
        """
        Averages the E2E test results from a collection of result files.

        Parameters
        ----------
        results_paths : list[Path]
            The paths to the E2E result files to average.

        Notes
        -----
        Loads and validates the result files and uses the first result file as the reference structure. Outputs that are
        missing from one or more runs or have invalid value structures are excluded from the averaged results. Outputs
        that do not contain a ``values`` list are preserved when they are identical across all runs. Numeric values
        within valid ``values`` lists are averaged across runs, while non-numeric values are preserved from the
        reference result.

        Returns
        -------
        dict[str, Any]
            The averaged E2E test results, retaining the structure and metadata of the reference result where
            applicable.
        """
        test_results = E2ETestResultsHandler._load_results(results_paths)

        reference_results = test_results[0]
        reference_keys = set(reference_results)

        E2ETestResultsHandler._validate_results(
            results_paths,
            test_results,
            reference_keys,
        )

        averaged_results: dict[str, Any] = {}

        for output_name, reference_output in reference_results.items():
            if output_name == "DISCLAIMER":
                averaged_results[output_name] = reference_output
                continue

            missing_results_paths = [
                result_path for result_path, result in zip(results_paths, test_results) if output_name not in result
            ]

            if missing_results_paths:
                OutputManager().add_warning(
                    "E2E Results Averaging Warning",
                    (
                        f"E2E output '{output_name}' is missing from "
                        f"{len(missing_results_paths)} of {len(test_results)} runs "
                        "and will be excluded from the averaged results. "
                        f"Missing from: {missing_results_paths}."
                    ),
                    info_map={
                        "class": E2ETestResultsHandler.__class__.__name__,
                        "function": E2ETestResultsHandler._average_test_results.__name__,
                    },
                )
                continue

            matching_outputs = [result[output_name] for result in test_results]

            if not isinstance(reference_output, dict) or "values" not in reference_output:
                if not all(output == reference_output for output in matching_outputs):
                    OutputManager().add_warning(
                        "E2E Results Averaging Error",
                        f"Non-matching data in reference output for {output_name}",
                        info_map={
                            "class": E2ETestResultsHandler.__class__.__name__,
                            "function": E2ETestResultsHandler._average_test_results.__name__,
                        },
                    )
                    continue

                averaged_results[output_name] = reference_output
                continue

            reference_values = reference_output["values"]

            values_are_valid = E2ETestResultsHandler._validate_values(
                results_paths,
                output_name,
                matching_outputs,
                reference_values,
            )

            if not values_are_valid:
                continue

            averaged_values = E2ETestResultsHandler._average_output_values(
                output_name,
                reference_values,
                matching_outputs,
            )

            averaged_results[output_name] = {
                **reference_output,
                "values": averaged_values,
            }

        return averaged_results

    @staticmethod
    def _average_output_values(
        output_name: str,
        reference_values: list[Any],
        matching_outputs: list[dict[str, Any]],
    ) -> list[Any]:
        """
        Averages the values for a single E2E output across multiple test runs.

        Parameters
        ----------
        output_name : str
            The name of the E2E output being averaged.
        reference_values : list[Any]
            The values from the reference E2E result.
        matching_outputs : list[dict[str, Any]]
            The corresponding E2E outputs from each test run.

        Notes
        -----
        Numeric values are averaged across runs after excluding NaN values. If all numeric values are identical, the
        reference value is preserved without conversion. Non-numeric values are not averaged and the reference value is
        preserved. If numeric types are inconsistent or non-numeric values differ between runs, a warning is logged and
        the reference value is retained.

        Returns
        -------
        list[Any]
            The averaged values for the E2E output, with reference values retained where averaging is not applicable.
        """
        averaged_values: list[Any] = []

        for index, reference_value in enumerate(reference_values):
            matching_values = [output["values"][index] for output in matching_outputs]

            is_numeric = isinstance(reference_value, Number) and not isinstance(reference_value, bool)

            if not is_numeric:
                if not all(value == reference_value for value in matching_values):
                    OutputManager().add_warning(
                        "E2E Results Averaging Error",
                        f"Non-numeric values differ for '{output_name}' at index {index}.",
                        info_map={
                            "class": E2ETestResultsHandler.__class__.__name__,
                            "function": E2ETestResultsHandler._average_output_values.__name__,
                        },
                    )

                averaged_values.append(reference_value)
                continue

            if not all(isinstance(value, Number) and not isinstance(value, bool) for value in matching_values):
                OutputManager().add_warning(
                    "E2E Results Averaging Error",
                    (
                        f"Inconsistent numeric value types for '{output_name}' at index {index}. "
                        f"Values: {matching_values}. "
                        f"Types: {[type(value).__name__ for value in matching_values]}."
                    ),
                    info_map={
                        "class": E2ETestResultsHandler.__class__.__name__,
                        "function": E2ETestResultsHandler._average_output_values.__name__,
                    },
                )

                averaged_values.append(reference_value)
                continue

            if all(value == reference_value for value in matching_values):
                averaged_values.append(reference_value)
                continue

            numeric_values = [float(value) for value in matching_values if not math.isnan(float(value))]

            averaged_value = sum(numeric_values) / len(numeric_values) if numeric_values else float("nan")

            averaged_values.append(averaged_value)

        return averaged_values

    @staticmethod
    def _validate_values(
        result_paths: list[Path],
        output_name: str,
        matching_outputs: list[dict[str, Any]],
        reference_values: list[Any],
    ) -> bool:
        """
        Validates the value structures for a single E2E output across multiple test runs.

        Parameters
        ----------
        result_paths : list[Path]
            The paths to the E2E result files containing the outputs being validated.
        output_name : str
            The name of the E2E output being validated.
        matching_outputs : list[dict[str, Any]]
            The corresponding E2E outputs from each test run.
        reference_values : list[Any]
            The values from the reference E2E output used to determine the expected number of values.

        Notes
        -----
        Verifies that each matching output contains a ``values`` list and that the number of values matches the number
        in the reference output. If an output does not contain a ``values`` list, an error is logged and validation
        immediately fails. If an output contains a different number of values, a warning is logged and validation
        continues so that all matching outputs can be checked.

        Returns
        -------
        bool
            True if every matching output contains a ``values`` list with the expected number of values, otherwise
            False.
        """
        values_are_valid = True

        for result_path, output in zip(result_paths, matching_outputs):
            if not isinstance(output, dict) or "values" not in output:
                OutputManager().add_error(
                    "E2E Results Averaging Error",
                    f"E2E output '{output_name}' in '{result_path}' does not contain a 'values' list.",
                    info_map={
                        "class": E2ETestResultsHandler.__class__.__name__,
                        "function": E2ETestResultsHandler._validate_values.__name__,
                    },
                )
                return False

            if len(output["values"]) != len(reference_values):
                OutputManager().add_warning(
                    "E2E Results Averaging Error",
                    (
                        f"E2E output '{output_name}' has {len(output['values'])} values "
                        f"in '{result_path}', but {len(reference_values)} were expected."
                    ),
                    info_map={
                        "class": E2ETestResultsHandler.__class__.__name__,
                        "function": E2ETestResultsHandler._validate_values.__name__,
                    },
                )
                values_are_valid = False

        return values_are_valid

    @staticmethod
    def _validate_results(
        result_paths: list[Path],
        test_results: list[dict[str, Any]],
        reference_keys: set[str],
    ) -> None:
        """
        Validates the structure of E2E test results against the reference result.

        Parameters
        ----------
        result_paths : list[Path]
            The paths to the E2E result files being validated.
        test_results : list[dict[str, Any]]
            The loaded E2E test results. The first result is treated as the reference result and is not validated
            against itself.
        reference_keys : set[str]
            The top-level keys from the reference E2E result that are expected in the other results.

        Notes
        -----
        Compares the top-level keys of each test result after the reference result with the expected reference keys. A
        warning is logged for any result containing missing or unexpected keys. Structural differences are reported but
        do not stop validation or raise an exception.
        """
        for result_path, result in zip(
            result_paths[1:],
            test_results[1:],
        ):
            result_keys = set(result)

            missing_keys = reference_keys - result_keys
            unexpected_keys = result_keys - reference_keys

            if missing_keys or unexpected_keys:
                OutputManager().add_warning(
                    "E2E Results Averaging Warning",
                    (
                        f"E2E result structure differs for "
                        f"'{result_path}'. "
                        f"Missing keys: {sorted(missing_keys)}. "
                        f"Unexpected keys: {sorted(unexpected_keys)}."
                    ),
                    info_map={
                        "class": (E2ETestResultsHandler.__class__.__name__),
                        "function": (E2ETestResultsHandler._validate_results.__name__),
                    },
                )

    @staticmethod
    def _load_results(result_paths: list[Path]) -> list[dict[str, Any]]:
        """
        Loads E2E test results from JSON files.

        Reads each provided JSON result file and collects the deserialized contents in the same order as the provided
        paths.

        Parameters
        ----------
        result_paths : list[Path]
            The paths to the JSON result files to load.

        Returns
        -------
        list[dict[str, Any]]
            The loaded E2E test results in the same order as ``result_paths``.
        """
        test_results: list[dict[str, Any]] = []

        for result_path in result_paths:
            with open(result_path, "r", encoding="utf-8") as result_file:
                test_results.append(json.load(result_file))
        return test_results

    @staticmethod
    def _extract_results_paths(
        e2e_runs: list[dict[str, Any]],
        json_output_directory: Path,
        actual_results_path: Path,
    ) -> list[Path]:
        """
        Extracts the result file corresponding to each E2E run for a specific E2E output.

        Parameters
        ----------
        e2e_runs : list[dict[str, Any]]
            The E2E run configurations for which result files should be located. Each run must contain an
            ``output_prefix`` and ``e2e_group``.
        json_output_directory : Path
            The directory containing the generated E2E JSON result files.
        actual_results_path : Path
            The configured actual results path used to determine the result filename associated with each E2E run.

        Notes
        -----
        Determines the expected result filename prefix for each E2E run using the run's output prefix and the provided
        actual results path. Searches the JSON output directory for the corresponding result file and requires exactly
        one matching file for each run.

        Returns
        -------
        list[Path]
            The matching E2E result file paths, in the same order as ``e2e_runs``.

        Raises
        ------
        ValueError
            If exactly one matching result file cannot be found for any E2E run.
        """
        result_paths: list[Path] = []

        for run in e2e_runs:
            run_output_prefix = run["output_prefix"]
            e2e_group = run["e2e_group"]

            result_name = actual_results_path.name.removeprefix(f"{e2e_group}_")

            expected_prefix = f"{run_output_prefix}_" f"{result_name}"

            matching_paths = [path for path in json_output_directory.iterdir() if path.name.startswith(expected_prefix)]

            if len(matching_paths) != 1:
                OutputManager().add_error(
                    "E2E Results Averaging Error",
                    (
                        f"Expected exactly one E2E result file for "
                        f"'{run_output_prefix}' matching "
                        f"'{result_name}', but found "
                        f"{len(matching_paths)}."
                    ),
                    info_map={
                        "class": E2ETestResultsHandler.__class__.__name__,
                        "function": E2ETestResultsHandler._extract_results_paths.__name__,
                    },
                )
                raise ValueError(
                    f"Expected exactly one E2E result file for "
                    f"'{run_output_prefix}' matching "
                    f"'{result_name}', but found "
                    f"{len(matching_paths)}."
                )

            result_paths.append(matching_paths[0])

        return result_paths

    @staticmethod
    def _convert_expected_result_variable_names(
        expected_results: dict[str, Any], conversion_csv_path: Path
    ) -> dict[str, Any]:
        """
        Convert variable names in the ``expected_results`` dictionary using a CSV-based conversion table.

        Parameters
        ----------
        expected_results : dict[str, Any]
            A dictionary where the keys represent the original variable names and the values are
            the associated data.
        conversion_csv_path : Path
            The file path to the conversion CSV containing the mapping of original variable names
            to new variable names.

        Returns
        -------
        dict[str, Any]
            A dictionary with updated keys based on the conversion mappings from the CSV. If a key
            in ``expected_results`` is not found in the mapping, it is preserved in the returned dictionary.

        Raises
        ------
        KeyError
            Raised if the conversion table CSV does not contain both "Original" and "New" columns.
        ValueError
            Raised if the conversion table CSV contains duplicate mappings for original variable names.

        Notes
        -----
        Reads a CSV file containing mappings of original variable names to new variable names and applies
        these mappings to the keys in the given dictionary ``expected_results``. The conversion table must
        contain two columns: "Original" and "New". Ensures no duplicate mappings exist in the CSV and raises
        appropriate errors otherwise. Returns a dictionary with updated keys while preserving their associated
        values.
        """
        om: OutputManager = OutputManager()
        info_map: dict[str, Any] = {
            "class": E2ETestResultsHandler.__name__,
            "function": E2ETestResultsHandler._convert_expected_result_variable_names.__name__,
        }

        converted_expected_results: dict[str, Any] = {}
        df_conversion_lookup_table: pd.DataFrame = pd.read_csv(conversion_csv_path, index_col=None)
        if "Original" not in df_conversion_lookup_table.columns or "New" not in df_conversion_lookup_table.columns:
            om.add_error(
                "Conversion Table Key Error",
                "The conversion table CSV should have both 'Original' and 'New' columns.",
                info_map,
            )
            raise KeyError("E2E testing error: The conversion table CSV should have both 'Original' and 'New' columns.")
        if E2ETestResultsHandler._duplicate_mappings_exist(df_conversion_lookup_table):
            raise ValueError(
                "E2E testing error: Duplicate Mapping Error: The conversion table CSV should not contain "
                "duplicate mappings."
            )
        conversion_lookup_table: dict[str, str] = df_conversion_lookup_table.set_index("Original")["New"].to_dict()
        for key, value in expected_results.items():
            if key in list(conversion_lookup_table.keys()):
                new_key = conversion_lookup_table[key]
                converted_expected_results[new_key] = value
            else:
                converted_expected_results[key] = value
        return converted_expected_results

    @staticmethod
    def _find_duplicate_mappings(
        mapping: pd.DataFrame, group_column_name: str, list_column_name: str
    ) -> dict[str, list[str]]:
        """
        Identifies entries in a ``DataFrame`` where a single key maps to multiple values.

        Parameters
        ----------
        mapping : pd.DataFrame
            The ``DataFrame`` containing the mapping data. Must include the specified columns.
        group_column_name : str
            The column to be analyzed for duplicate mappings.
        list_column_name : str
            The column containing values that are mapped from ``group_column_name``.

        Returns
        -------
        dict[str, list[str]]
            A dictionary where each key is a duplicated entry from ``group_column_name``,
            and each value is a list of corresponding mapped values from ``list_column_name``.

        Notes
        -----
        This method examines a ``DataFrame`` containing mappings between two columns and
        finds instances where a value in the ``group_column_name`` column is associated
        with more than one unique value in the ``list_column_name`` column.

        The result is a dictionary where:
          - Keys are the duplicated values from ``group_column_name``.
          - Values are lists of corresponding values from ``list_column_name``.
        """
        grouped: dict[str, list[str]] = mapping.groupby(group_column_name)[list_column_name].apply(list).to_dict()

        duplicates: dict[str, list[str]] = {
            group_val: mapped_vals for group_val, mapped_vals in grouped.items() if len(mapped_vals) > 1
        }
        return duplicates

    @staticmethod
    def _duplicate_mappings_exist(mapping: pd.DataFrame) -> bool:
        """
        Checks for duplicate mappings in the provided ``DataFrame`` and logs errors if any
        duplicates are found. This ensures that no original variable name maps to multiple new
        variable names, and no new variable name is mapped from multiple original variable names.

        Parameters
        ----------
        mapping : pd.DataFrame
            A ``DataFrame`` containing the mappings between ``Original`` and ``New`` variable names.

        Returns
        -------
        bool
            If any duplicate mappings are found, returns ``True``. Otherwise, returns ``False``.
        """
        info_map: dict[str, str] = {
            "class": E2ETestResultsHandler.__name__,
            "function": E2ETestResultsHandler._duplicate_mappings_exist.__name__,
        }
        om = OutputManager()

        duplicates_in_original_column: dict[str, list[str]] = E2ETestResultsHandler._find_duplicate_mappings(
            mapping, group_column_name="Original", list_column_name="New"
        )
        duplicates_in_new_column: dict[str, list[str]] = E2ETestResultsHandler._find_duplicate_mappings(
            mapping, group_column_name="New", list_column_name="Original"
        )
        for original_name, new_names in duplicates_in_original_column.items():
            om.add_error(
                "Duplicate Mapping Error",
                f"Original variable name: '{original_name}' is mapping to multiple new variable names: {new_names}",
                info_map,
            )

        for new_name, original_names in duplicates_in_new_column.items():
            om.add_error(
                "Duplicate Mapping Error",
                f"New variable name: '{new_name}' is mapped from multiple original variable names: {original_names}",
                info_map,
            )
        return len(duplicates_in_original_column) > 0 or len(duplicates_in_new_column) > 0

    @staticmethod
    def _get_test_result_paths(output_prefix: str) -> list[ResultPathType]:
        """
        Retrieves the paths to test results and associated information from the InputManager.

        Parameters
        ----------
        output_prefix : str
            The output prefix.

        Returns
        -------
        list[ResultPathType]
            List of result path sets, each containing the domain, expected results path,
            actual results path, tolerance, and the optional must-change variables, accepted ranges, and variable
            tolerances file paths and tolerance type for one test domain.
        """
        im = InputManager()
        result_paths: list[dict[str, str]] = im.get_data(
            f"end_to_end_testing_result_paths.end_to_end_test_result_paths.{output_prefix}"
        )
        test_result_paths: list[ResultPathType] = []
        for path_set in result_paths:
            test_result_paths.append(
                ResultPathType(
                    path_set["domain"],
                    path_set["expected_results_path"],
                    path_set["actual_results_path"],
                    path_set["tolerance"],
                    path_set.get("must_change_variables_path", ""),
                    path_set.get("accepted_ranges_path", ""),
                    path_set.get("tolerance_type", TOLERANCE_TYPE_PERCENT),
                    path_set.get("variable_tolerances_path", ""),
                )
            )
        return test_result_paths

    @staticmethod
    def _load_must_change_variables(test_result_path_sets: list[ResultPathType]) -> set[str]:
        """
        Loads the names of the variables flagged as must change for an end-to-end testing input set.

        Parameters
        ----------
        test_result_path_sets : list[ResultPathType]
            List of result path sets for the input set, each optionally referencing a must-change variables file
            through its ``must_change_variables_path`` field.

        Returns
        -------
        set[str]
            The union of the variable names listed in the referenced must-change variables files. Path sets with an
            empty ``must_change_variables_path`` are skipped.

        Raises
        ------
        FileNotFoundError
            If a referenced must-change variables file does not exist.
        ValueError
            If a referenced file is not valid JSON, or does not contain a list of strings under the
            ``must_change_variables`` key.
        """
        om = OutputManager()
        info_map: dict[str, Any] = {
            "class": E2ETestResultsHandler.__name__,
            "function": E2ETestResultsHandler._load_must_change_variables.__name__,
        }
        must_change_variables: set[str] = set()
        must_change_paths = {
            path_set.must_change_variables_path
            for path_set in test_result_path_sets
            if path_set.must_change_variables_path
        }
        for path_str in sorted(must_change_paths):
            path = Path(path_str)
            if not path.exists():
                om.add_error(
                    "End-to-end testing must-change configuration error",
                    f"Must-change variables file not found: {path}",
                    info_map,
                )
                raise FileNotFoundError(f"E2E testing error: Must-change variables file not found: {path}")
            try:
                with open(path, "r", encoding="utf-8") as must_change_file:
                    file_contents = json.load(must_change_file)
            except json.JSONDecodeError as e:
                om.add_error(
                    "End-to-end testing must-change configuration error",
                    f"Must-change variables file {path} is not valid JSON: {e}",
                    info_map,
                )
                raise ValueError(f"E2E testing error: Must-change variables file {path} is not valid JSON.") from e
            variable_names = file_contents.get(MUST_CHANGE_VARIABLES_KEY) if isinstance(file_contents, dict) else None
            if not isinstance(variable_names, list) or not all(isinstance(name, str) for name in variable_names):
                om.add_error(
                    "End-to-end testing must-change configuration error",
                    f"Must-change variables file {path} must contain a list of variable names under the "
                    f"'{MUST_CHANGE_VARIABLES_KEY}' key.",
                    info_map,
                )
                raise ValueError(
                    f"E2E testing error: Must-change variables file {path} must contain a list of variable names "
                    f"under the '{MUST_CHANGE_VARIABLES_KEY}' key."
                )
            must_change_variables.update(variable_names)
        return must_change_variables

    @staticmethod
    def _load_expected_results_file(
        path_set: ResultPathType, convert_variable_table_path: str | None = None
    ) -> dict[str, Any]:
        """
        Loads the expected results file of a domain.

        Parameters
        ----------
        path_set : ResultPathType
            The result path set of the domain, referencing the expected results file through its
            ``expected_results_path`` field.
        convert_variable_table_path : str | None, optional
            String path to the csv lookup table to convert the variable names in the expected results to match the
            variable names in the actual results. No conversion is applied when ``None`` (the default).

        Returns
        -------
        dict[str, Any]
            The content of the expected results file, with the variable names of its ``expected_results`` converted
            when a conversion table is given.

        Raises
        ------
        FileNotFoundError
            If the expected results file does not exist.
        ValueError
            If the expected results file is not valid JSON, e.g. because it still starts with the warning line written
            by ``update_expected_test_results``.
        KeyError
            If the expected results file has no ``expected_results`` entry.
        """
        with open(f"{path_set.expected_results_path}", "r", encoding="utf-8") as e_to_e_results:
            filter_and_results: dict[str, Any] = json.load(e_to_e_results)
            expected_results = filter_and_results["expected_results"]
            if convert_variable_table_path is not None:
                expected_results = E2ETestResultsHandler._convert_expected_result_variable_names(
                    expected_results=expected_results, conversion_csv_path=Path(convert_variable_table_path)
                )
        filter_and_results["expected_results"] = expected_results
        return filter_and_results

    @staticmethod
    def _record_configuration_error(errors: list[str], message: str) -> None:
        """Appends a configuration problem to ``errors``, without the common message prefix and without duplicates."""
        message = message.removeprefix("E2E testing error: ")
        if message not in errors:
            errors.append(message)

    @staticmethod
    def _raise_configuration_errors(errors: list[str]) -> None:
        """
        Raises a single error listing every configuration problem recorded by a validation.

        Parameters
        ----------
        errors : list[str]
            The configuration problems recorded by the validation.

        Raises
        ------
        ValueError
            Always, with a message listing every problem in ``errors``.
        """
        raise ValueError(
            "E2E testing error: invalid end-to-end testing configuration:\n"
            + "\n".join(f"  - {error}" for error in errors)
        )

    @staticmethod
    def _record_unknown_variables(
        errors: list[str], error_title: str, description: str, unknown_names: set[str], info_map: dict[str, Any]
    ) -> None:
        """
        Records the variable names of a comparison feature that are not found in the expected results of any domain.

        Parameters
        ----------
        errors : list[str]
            The list that the problem is appended to, so that the caller can report every problem together.
        error_title : str
            The title of the error logged through the ``OutputManager``.
        description : str
            How the variables are referred to in the message, e.g. ``"Must-change variables"``.
        unknown_names : set[str]
            The variable names that are not found. Nothing is recorded when the set is empty.
        info_map : dict[str, Any]
            Information about the source of the logged error.
        """
        if not unknown_names:
            return
        message = f"{description} not found in the expected results of any domain: {sorted(unknown_names)}"
        OutputManager().add_error(error_title, message, info_map)
        E2ETestResultsHandler._record_configuration_error(errors, message)

    @staticmethod
    def _validate_result_path_set(
        path_set: ResultPathType,
        output_prefix: str,
        filters_directory: Path,
        errors: list[str],
        convert_variable_table_path: str | None = None,
    ) -> dict[str, Any] | None:
        """
        Checks that a domain's result path set can be resolved once the simulation has run.

        Parameters
        ----------
        path_set : ResultPathType
            The result path set of the domain.
        output_prefix : str
            The output prefix of the end-to-end testing input set, which prefixes the run's output file names.
        filters_directory : Path
            The directory the task loads its filter files from.
        errors : list[str]
            The list that every problem found is appended to, so that the caller can report them all together.
        convert_variable_table_path : str | None, optional
            String path to the csv lookup table to convert the variable names in the expected results, passed on to
            ``_load_expected_results_file``. No conversion is applied when ``None`` (the default).

        Returns
        -------
        dict[str, Any] | None
            The content of the domain's expected results file, as returned by ``_load_expected_results_file``, or
            ``None`` when the file could not be loaded.

        Notes
        -----
        The expected results file doubles as the filter that collects the domain's actual results, so it has to be in
        the task's filters directory, and the run writes those actual results to
        ``{output_prefix}_saved_variables_{filter name}_{timestamp}.json``, which ``actual_results_path`` has to match
        as a prefix for the results to be found afterwards. When the filter name is unknown because the expected
        results file could not be loaded, ``actual_results_path`` is only checked against the part of the file name
        that does not depend on it, ``{output_prefix}_saved_variables_``. The domain's ``tolerance`` also has to be
        valid for its ``tolerance_type`` (see ``_is_valid_tolerance``).
        """
        om = OutputManager()
        info_map: dict[str, Any] = {
            "class": E2ETestResultsHandler.__name__,
            "function": E2ETestResultsHandler._validate_result_path_set.__name__,
            "domain": path_set.domain,
        }
        error_title = f"End-to-end testing configuration error for {path_set.domain}"
        expected_results_path = Path(path_set.expected_results_path)
        file_content: dict[str, Any] | None = None
        try:
            file_content = E2ETestResultsHandler._load_expected_results_file(path_set, convert_variable_table_path)
        except (OSError, ValueError, KeyError, TypeError) as e:
            message = (
                f"Expected results file {expected_results_path} for {path_set.domain} could not be loaded: "
                f"{type(e).__name__}: {e}"
            )
            om.add_error(error_title, message, info_map)
            E2ETestResultsHandler._record_configuration_error(errors, message)

        if file_content is not None and expected_results_path.resolve().parent != Path(filters_directory).resolve():
            message = (
                f"Expected results file {expected_results_path} is not in the task's filters directory "
                f"{filters_directory}, so the run will not collect the domain's actual results from it."
            )
            om.add_error(error_title, message, info_map)
            E2ETestResultsHandler._record_configuration_error(errors, message)

        filter_name = file_content.get("name") if file_content is not None else None
        actual_results_path_name = Path(path_set.actual_results_path).name
        if filter_name is not None:
            actual_results_file_prefix = f"{output_prefix}_saved_variables_{filter_name}_"
            is_matching = actual_results_file_prefix.startswith(actual_results_path_name)
        else:
            actual_results_file_prefix = f"{output_prefix}_saved_variables_"
            is_matching = actual_results_file_prefix.startswith(
                actual_results_path_name
            ) or actual_results_path_name.startswith(actual_results_file_prefix)
        if not actual_results_path_name or not is_matching:
            message = (
                f"actual_results_path '{path_set.actual_results_path}' for {path_set.domain} does not match the "
                f"actual results file name the run will write, which starts with '{actual_results_file_prefix}'."
            )
            om.add_error(error_title, message, info_map)
            E2ETestResultsHandler._record_configuration_error(errors, message)
        if not E2ETestResultsHandler._is_valid_tolerance(path_set.tolerance, path_set.tolerance_type):
            message = (
                f"tolerance '{path_set.tolerance}' with tolerance_type '{path_set.tolerance_type}' for "
                f"{path_set.domain} is not valid: {TOLERANCE_REQUIREMENTS}."
            )
            om.add_error(error_title, message, info_map)
            E2ETestResultsHandler._record_configuration_error(errors, message)
        return file_content

    @staticmethod
    def _evaluate_must_change_variables(
        expected_results: dict[str, Any],
        actual_results: dict[str, Any],
        must_change_variable_names: list[str],
        tolerance: float,
        tolerance_type: str = TOLERANCE_TYPE_PERCENT,
        variable_tolerances: dict[str, dict[str, Any]] | None = None,
    ) -> tuple[list[str], dict[str, str]]:
        """
        Checks that each variable flagged as must change actually differs from its recorded expected value.

        Parameters
        ----------
        expected_results : dict[str, Any]
            The expected results for a domain, keyed by variable name.
        actual_results : dict[str, Any]
            The actual results for a domain, keyed by variable name.
        must_change_variable_names : list[str]
            The must-change variable names present in ``expected_results``.
        tolerance : float
            The domain threshold below which a difference is considered no change, interpreted according to
            ``tolerance_type``.
        tolerance_type : str, optional
            How ``tolerance`` is interpreted, one of ``TOLERANCE_TYPES`` (see ``_exceeds_tolerance``). Defaults to
            ``percent``.
        variable_tolerances : dict[str, dict[str, Any]] | None, optional
            Tolerance overrides keyed by variable name, applied to the flagged variables they list instead of the
            domain tolerance (see ``filter_nested``). ``None`` (the default) applies the domain tolerance to all.

        Returns
        -------
        tuple[list[str], dict[str, str]]
            A list of the must-change variables whose values differ from the expected results, and a dictionary
            mapping each violating must-change variable to the reason it failed: either its value still matches the
            expected results, or it is missing from the actual results.
        """
        must_change_satisfied: list[str] = []
        must_change_violations: dict[str, str] = {}
        for variable_name in must_change_variable_names:
            if variable_name not in actual_results:
                must_change_violations[variable_name] = (
                    "Flagged as must change but the variable is missing from the actual results."
                )
                continue
            pair_diff = DeepDiff(
                {variable_name: expected_results[variable_name]},
                {variable_name: actual_results[variable_name]},
                ignore_order=True,
                verbose_level=2,
                significant_digits=3,
            )
            filtered_pair_diff = E2ETestResultsHandler.filter_insignificant_changes(
                pair_diff, tolerance, tolerance_type, variable_tolerances
            )
            if filtered_pair_diff == {}:
                must_change_violations[variable_name] = (
                    "Flagged as must change but the value still matches the expected results within the tolerance."
                )
            else:
                must_change_satisfied.append(variable_name)
        return must_change_satisfied, must_change_violations

    @staticmethod
    def _load_accepted_ranges(test_result_path_sets: list[ResultPathType]) -> dict[str, dict[str, Any]]:
        """
        Loads the accepted ranges of the variables of an end-to-end testing input set.

        Parameters
        ----------
        test_result_path_sets : list[ResultPathType]
            List of result path sets for the input set, each optionally referencing an accepted ranges file through
            its ``accepted_ranges_path`` field.

        Returns
        -------
        dict[str, dict[str, Any]]
            The accepted ranges read from the referenced files, keyed by variable name. Each range is the entry
            recorded in the file, holding at least its numerical ``min`` and ``max`` bounds. Path sets with an empty
            ``accepted_ranges_path`` are skipped.

        Raises
        ------
        FileNotFoundError
            If a referenced accepted ranges file does not exist.
        ValueError
            If a referenced file is not valid JSON, does not contain a dictionary of ranges under the
            ``accepted_ranges`` key, or contains a range without numerical ``min`` and ``max`` bounds where ``min``
            is no greater than ``max``.
        """
        om = OutputManager()
        info_map: dict[str, Any] = {
            "class": E2ETestResultsHandler.__name__,
            "function": E2ETestResultsHandler._load_accepted_ranges.__name__,
        }
        error_title = "End-to-end testing accepted-range configuration error"
        accepted_ranges: dict[str, dict[str, Any]] = {}
        accepted_ranges_paths = {
            path_set.accepted_ranges_path for path_set in test_result_path_sets if path_set.accepted_ranges_path
        }
        for path_str in sorted(accepted_ranges_paths):
            path = Path(path_str)
            if not path.exists():
                om.add_error(error_title, f"Accepted ranges file not found: {path}", info_map)
                raise FileNotFoundError(f"E2E testing error: Accepted ranges file not found: {path}")
            try:
                with open(path, "r", encoding="utf-8") as accepted_ranges_file:
                    file_contents = json.load(accepted_ranges_file)
            except json.JSONDecodeError as e:
                om.add_error(error_title, f"Accepted ranges file {path} is not valid JSON: {e}", info_map)
                raise ValueError(f"E2E testing error: Accepted ranges file {path} is not valid JSON.") from e
            file_ranges = file_contents.get(ACCEPTED_RANGES_KEY) if isinstance(file_contents, dict) else None
            if not isinstance(file_ranges, dict):
                message = (
                    f"Accepted ranges file {path} must contain a dictionary of variable ranges under the "
                    f"'{ACCEPTED_RANGES_KEY}' key."
                )
                om.add_error(error_title, message, info_map)
                raise ValueError(f"E2E testing error: {message}")
            invalid_ranges = sorted(
                name
                for name, accepted_range in file_ranges.items()
                if not E2ETestResultsHandler._is_valid_accepted_range(accepted_range)
            )
            if invalid_ranges:
                message = (
                    f"Accepted ranges file {path} has invalid ranges for {invalid_ranges}: each range must have "
                    f"numerical '{ACCEPTED_RANGE_MIN_KEY}' and '{ACCEPTED_RANGE_MAX_KEY}' bounds, with "
                    f"'{ACCEPTED_RANGE_MIN_KEY}' no greater than '{ACCEPTED_RANGE_MAX_KEY}'."
                )
                om.add_error(error_title, message, info_map)
                raise ValueError(f"E2E testing error: {message}")
            accepted_ranges.update(file_ranges)
        return accepted_ranges

    @staticmethod
    def _collect_accepted_ranges(
        test_result_path_sets: list[ResultPathType], errors: list[str]
    ) -> dict[str, dict[str, Any]]:
        """
        Loads every accepted ranges file of an input set, recording the files that cannot be loaded.

        Parameters
        ----------
        test_result_path_sets : list[ResultPathType]
            List of result path sets for the input set, each optionally referencing an accepted ranges file through
            its ``accepted_ranges_path`` field.
        errors : list[str]
            The list that the problem of every file that cannot be loaded is appended to, so that the caller can
            report them all together.

        Returns
        -------
        dict[str, dict[str, Any]]
            The accepted ranges read from the files that could be loaded, keyed by variable name.

        Notes
        -----
        Each distinct file is loaded on its own with ``_load_accepted_ranges``, so that one unreadable file does not
        hide the problems of another.
        """
        accepted_ranges: dict[str, dict[str, Any]] = {}
        checked_accepted_ranges_paths: set[str] = set()
        for path_set in test_result_path_sets:
            if path_set.accepted_ranges_path in checked_accepted_ranges_paths:
                continue
            checked_accepted_ranges_paths.add(path_set.accepted_ranges_path)
            try:
                accepted_ranges.update(E2ETestResultsHandler._load_accepted_ranges([path_set]))
            except (FileNotFoundError, ValueError) as e:
                E2ETestResultsHandler._record_configuration_error(errors, str(e))
        return accepted_ranges

    @staticmethod
    def _is_valid_accepted_range(accepted_range: Any) -> bool:
        """
        Checks that an accepted range entry has numerical bounds in the right order.

        Parameters
        ----------
        accepted_range : Any
            The range entry read from an accepted ranges file.

        Returns
        -------
        bool
            ``True`` if the entry is a dictionary with numerical ``min`` and ``max`` bounds where ``min`` is no
            greater than ``max``, ``False`` otherwise. Any other keys of the entry are ignored.
        """
        if not isinstance(accepted_range, dict):
            return False
        lower_bound = accepted_range.get(ACCEPTED_RANGE_MIN_KEY)
        upper_bound = accepted_range.get(ACCEPTED_RANGE_MAX_KEY)
        if DataValidator.is_number(lower_bound) and DataValidator.is_number(upper_bound):
            return lower_bound <= upper_bound
        return False

    @staticmethod
    def _load_variable_tolerances(test_result_path_sets: list[ResultPathType]) -> dict[str, dict[str, Any]]:
        """
        Loads the tolerance overrides of the variables of an end-to-end testing input set.

        Parameters
        ----------
        test_result_path_sets : list[ResultPathType]
            List of result path sets for the input set, each optionally referencing a variable tolerances file
            through its ``variable_tolerances_path`` field.

        Returns
        -------
        dict[str, dict[str, Any]]
            The tolerance overrides read from the referenced files, keyed by variable name. Each override is the
            entry recorded in the file, holding its ``tolerance`` and its ``tolerance_type``, which is filled in with
            ``percent`` when the file leaves it out. Path sets with an empty ``variable_tolerances_path`` are
            skipped.

        Raises
        ------
        FileNotFoundError
            If a referenced variable tolerances file does not exist.
        ValueError
            If a referenced file is not valid JSON, does not contain a dictionary of overrides under the
            ``variable_tolerances`` key, or contains an override without a valid ``tolerance`` for its
            ``tolerance_type`` (see ``_is_valid_tolerance``).
        """
        om = OutputManager()
        info_map: dict[str, Any] = {
            "class": E2ETestResultsHandler.__name__,
            "function": E2ETestResultsHandler._load_variable_tolerances.__name__,
        }
        error_title = "End-to-end testing tolerance configuration error"
        variable_tolerances: dict[str, dict[str, Any]] = {}
        variable_tolerances_paths = {
            path_set.variable_tolerances_path for path_set in test_result_path_sets if path_set.variable_tolerances_path
        }
        for path_str in sorted(variable_tolerances_paths):
            path = Path(path_str)
            if not path.exists():
                om.add_error(error_title, f"Variable tolerances file not found: {path}", info_map)
                raise FileNotFoundError(f"E2E testing error: Variable tolerances file not found: {path}")
            try:
                with open(path, "r", encoding="utf-8") as variable_tolerances_file:
                    file_contents = json.load(variable_tolerances_file)
            except json.JSONDecodeError as e:
                om.add_error(error_title, f"Variable tolerances file {path} is not valid JSON: {e}", info_map)
                raise ValueError(f"E2E testing error: Variable tolerances file {path} is not valid JSON.") from e
            file_tolerances = file_contents.get(VARIABLE_TOLERANCES_KEY) if isinstance(file_contents, dict) else None
            if not isinstance(file_tolerances, dict):
                message = (
                    f"Variable tolerances file {path} must contain a dictionary of tolerance overrides under the "
                    f"'{VARIABLE_TOLERANCES_KEY}' key."
                )
                om.add_error(error_title, message, info_map)
                raise ValueError(f"E2E testing error: {message}")
            invalid_overrides = sorted(
                name
                for name, variable_tolerance in file_tolerances.items()
                if not E2ETestResultsHandler._is_valid_variable_tolerance(variable_tolerance)
            )
            if invalid_overrides:
                message = (
                    f"Variable tolerances file {path} has invalid tolerance overrides for {invalid_overrides}: each "
                    f"override must have a '{TOLERANCE_KEY}' and {TOLERANCE_REQUIREMENTS}."
                )
                om.add_error(error_title, message, info_map)
                raise ValueError(f"E2E testing error: {message}")
            for name, variable_tolerance in file_tolerances.items():
                variable_tolerances[name] = {TOLERANCE_TYPE_KEY: TOLERANCE_TYPE_PERCENT, **variable_tolerance}
        return variable_tolerances

    @staticmethod
    def _collect_variable_tolerances(
        test_result_path_sets: list[ResultPathType], errors: list[str]
    ) -> dict[str, dict[str, Any]]:
        """
        Loads every variable tolerances file of an input set, recording the files that cannot be loaded.

        Parameters
        ----------
        test_result_path_sets : list[ResultPathType]
            List of result path sets for the input set, each optionally referencing a variable tolerances file
            through its ``variable_tolerances_path`` field.
        errors : list[str]
            The list that the problem of every file that cannot be loaded is appended to, so that the caller can
            report them all together.

        Returns
        -------
        dict[str, dict[str, Any]]
            The tolerance overrides read from the files that could be loaded, keyed by variable name.

        Notes
        -----
        Each distinct file is loaded on its own with ``_load_variable_tolerances``, so that one unreadable file does
        not hide the problems of another.
        """
        variable_tolerances: dict[str, dict[str, Any]] = {}
        checked_variable_tolerances_paths: set[str] = set()
        for path_set in test_result_path_sets:
            if path_set.variable_tolerances_path in checked_variable_tolerances_paths:
                continue
            checked_variable_tolerances_paths.add(path_set.variable_tolerances_path)
            try:
                variable_tolerances.update(E2ETestResultsHandler._load_variable_tolerances([path_set]))
            except (FileNotFoundError, ValueError) as e:
                E2ETestResultsHandler._record_configuration_error(errors, str(e))
        return variable_tolerances

    @staticmethod
    def _is_valid_variable_tolerance(variable_tolerance: Any) -> bool:
        """
        Checks that a tolerance override entry has a valid tolerance for its tolerance type.

        Parameters
        ----------
        variable_tolerance : Any
            The override entry read from a variable tolerances file.

        Returns
        -------
        bool
            ``True`` if the entry is a dictionary whose ``tolerance`` is valid for its ``tolerance_type``, taken as
            ``percent`` when absent (see ``_is_valid_tolerance``), ``False`` otherwise. Any other keys of the entry
            are ignored.
        """
        if not isinstance(variable_tolerance, dict):
            return False
        return E2ETestResultsHandler._is_valid_tolerance(
            variable_tolerance.get(TOLERANCE_KEY), variable_tolerance.get(TOLERANCE_TYPE_KEY, TOLERANCE_TYPE_PERCENT)
        )

    @staticmethod
    def _is_valid_tolerance(tolerance: Any, tolerance_type: Any) -> bool:
        """
        Checks that a tolerance is valid for its tolerance type.

        Parameters
        ----------
        tolerance : Any
            The tolerance to check.
        tolerance_type : Any
            The tolerance type, expected to be one of ``TOLERANCE_TYPES``.

        Returns
        -------
        bool
            ``True`` if ``tolerance_type`` is one of ``TOLERANCE_TYPES`` and ``tolerance`` is a number of at least 0
            for ``percent`` and ``absolute``, or a whole number of at least 1 for ``significant_digits``; ``False``
            otherwise.
        """
        if tolerance_type not in TOLERANCE_TYPES or not DataValidator.is_number(tolerance):
            return False
        if tolerance_type == TOLERANCE_TYPE_SIGNIFICANT_DIGITS:
            return float(tolerance).is_integer() and tolerance >= 1
        return tolerance >= 0

    @staticmethod
    def _evaluate_accepted_ranges(
        actual_results: dict[str, Any], domain_accepted_ranges: dict[str, dict[str, Any]]
    ) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
        """
        Checks that every numerical value of each variable with an accepted range falls within its range.

        Parameters
        ----------
        actual_results : dict[str, Any]
            The actual results for a domain, keyed by variable name.
        domain_accepted_ranges : dict[str, dict[str, Any]]
            The accepted ranges of the variables present in the domain's expected results, keyed by variable name.

        Returns
        -------
        tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]
            The satisfied and the violated ranges, both keyed by variable name. Each entry is the accepted range
            extended with the observed minimum and maximum of the variable (``observed_min`` and ``observed_max``);
            a violated entry also holds the ``reason`` it failed: values outside the range, no numerical values to
            check, or the variable missing from the actual results.

        Notes
        -----
        The bounds are inclusive. The numerical values of a variable are collected from anywhere inside its recorded
        value (see ``_collect_numerical_values``), so the range applies to every number of a daily series or of a
        list of records alike.
        """
        accepted_range_satisfied: dict[str, dict[str, Any]] = {}
        accepted_range_violations: dict[str, dict[str, Any]] = {}
        for variable_name, accepted_range in domain_accepted_ranges.items():
            if variable_name not in actual_results:
                accepted_range_violations[variable_name] = {
                    **accepted_range,
                    "reason": "Assigned an accepted range but the variable is missing from the actual results.",
                }
                continue
            numerical_values = E2ETestResultsHandler._collect_numerical_values(actual_results[variable_name])
            if not numerical_values:
                accepted_range_violations[variable_name] = {
                    **accepted_range,
                    "reason": "Assigned an accepted range but the variable has no numerical values to check.",
                }
                continue
            range_outcome: dict[str, Any] = {
                **accepted_range,
                "observed_min": min(numerical_values),
                "observed_max": max(numerical_values),
            }
            lower_bound = accepted_range[ACCEPTED_RANGE_MIN_KEY]
            upper_bound = accepted_range[ACCEPTED_RANGE_MAX_KEY]
            out_of_range_count = sum(1 for value in numerical_values if not lower_bound <= value <= upper_bound)
            if out_of_range_count:
                range_outcome["reason"] = (
                    f"{out_of_range_count} of {len(numerical_values)} values fall outside the accepted range."
                )
                accepted_range_violations[variable_name] = range_outcome
            else:
                accepted_range_satisfied[variable_name] = range_outcome
        return accepted_range_satisfied, accepted_range_violations

    @staticmethod
    def _collect_numerical_values(value: Any) -> list[int | float]:
        """
        Collects the numbers nested anywhere inside a recorded variable value.

        Parameters
        ----------
        value : Any
            A recorded variable value, e.g. the ``{"values": [...]}`` dictionary of an end-to-end results file.

        Returns
        -------
        list[int | float]
            The numbers found, in traversal order. Lists and dictionary values are searched recursively; booleans,
            strings, and ``None`` are not numbers and are skipped.
        """
        if DataValidator.is_number(value):
            return [value]
        nested_values: Iterable[Any]
        if isinstance(value, dict):
            nested_values = value.values()
        elif isinstance(value, (list, tuple)):
            nested_values = value
        else:
            return []
        numerical_values: list[int | float] = []
        for nested_value in nested_values:
            numerical_values.extend(E2ETestResultsHandler._collect_numerical_values(nested_value))
        return numerical_values

    @staticmethod
    def _extract_changed_variable_names(diff_result: dict[str, Any]) -> list[str]:
        """
        Compiles the names of the variables that a ``DeepDiff`` result reports as different.

        Parameters
        ----------
        diff_result : dict[str, Any]
            A ``DeepDiff`` result mapping change categories (e.g. ``values_changed``) to changed paths.

        Returns
        -------
        list[str]
            The sorted, deduplicated top-level variable names extracted from the changed paths. Paths that do not
            start with a top-level dictionary key (e.g. a change to the results root) are skipped.
        """
        changed_variable_names: set[str] = set()
        for changed_entries in diff_result.values():
            if isinstance(changed_entries, dict):
                changed_paths = list(changed_entries.keys())
            elif isinstance(changed_entries, (list, set, tuple)):
                changed_paths = list(changed_entries)
            else:
                continue
            for changed_path in changed_paths:
                variable_name = E2ETestResultsHandler._get_top_level_variable_name(changed_path)
                if variable_name is not None:
                    changed_variable_names.add(variable_name)
        return sorted(changed_variable_names)

    @staticmethod
    def _get_top_level_variable_name(changed_path: Any) -> str | None:
        """
        Extracts the top-level variable name from a ``DeepDiff`` path such as ``root['name']['values'][3]``.

        Parameters
        ----------
        changed_path : Any
            A changed path reported by ``DeepDiff``.

        Returns
        -------
        str | None
            The top-level variable name, or ``None`` when the path does not start with a top-level dictionary key
            (e.g. a change to the results root).

        Notes
        -----
        ``DeepDiff`` writes a key containing a single quote between double quotes instead, so both quoting styles
        are recognized.
        """
        match = TOP_LEVEL_DIFF_PATH_PATTERN.match(str(changed_path))
        if match is None:
            return None
        return match.group(1) if match.group(1) is not None else match.group(2)

    @staticmethod
    def _resolve_tolerance(
        changed_path: str,
        tolerance: float,
        tolerance_type: str,
        variable_tolerances: dict[str, dict[str, Any]] | None,
    ) -> tuple[float, str]:
        """
        Picks the tolerance that applies to a changed ``DeepDiff`` path.

        Parameters
        ----------
        changed_path : str
            The changed path reported by ``DeepDiff``.
        tolerance : float
            The domain tolerance.
        tolerance_type : str
            The domain tolerance type, one of ``TOLERANCE_TYPES``.
        variable_tolerances : dict[str, dict[str, Any]] | None
            Tolerance overrides keyed by variable name, or ``None`` when there are none.

        Returns
        -------
        tuple[float, str]
            The ``tolerance`` and ``tolerance_type`` of the override of the path's top-level variable when there is
            one, the domain tolerance and tolerance type otherwise.
        """
        variable_name = E2ETestResultsHandler._get_top_level_variable_name(changed_path)
        if variable_tolerances and variable_name in variable_tolerances:
            variable_tolerance = variable_tolerances[variable_name]
            return variable_tolerance[TOLERANCE_KEY], variable_tolerance.get(TOLERANCE_TYPE_KEY, TOLERANCE_TYPE_PERCENT)
        return tolerance, tolerance_type

    @staticmethod
    def _exceeds_tolerance(old_value: float, new_value: float, tolerance: float, tolerance_type: str) -> bool:
        """
        Checks whether two numbers differ beyond a tolerance.

        Parameters
        ----------
        old_value : float
            The expected value.
        new_value : float
            The actual value.
        tolerance : float
            The tolerance, interpreted according to ``tolerance_type``.
        tolerance_type : str
            One of ``TOLERANCE_TYPES``: ``percent`` allows a difference of up to ``tolerance`` percent of the
            expected value (of 1 when the expected value is 0), ``absolute`` allows a difference of up to
            ``tolerance``, and ``significant_digits`` requires the two values to agree once rounded to ``tolerance``
            significant digits.

        Returns
        -------
        bool
            ``True`` if the values differ beyond the tolerance, ``False`` otherwise.

        Raises
        ------
        ValueError
            If ``tolerance_type`` is not one of ``TOLERANCE_TYPES``.
        """
        if tolerance_type == TOLERANCE_TYPE_SIGNIFICANT_DIGITS:
            significant_digits = int(tolerance)
            rounded_old_value = E2ETestResultsHandler._round_to_significant_digits(old_value, significant_digits)
            rounded_new_value = E2ETestResultsHandler._round_to_significant_digits(new_value, significant_digits)
            return rounded_old_value != rounded_new_value
        difference = abs(new_value - old_value)
        if tolerance_type == TOLERANCE_TYPE_ABSOLUTE:
            return difference > tolerance
        if tolerance_type == TOLERANCE_TYPE_PERCENT:
            reference = abs(old_value) if abs(old_value) > 0 else 1
            return difference > tolerance * GeneralConstants.PERCENTAGE_TO_FRACTION * reference
        raise ValueError(
            f"E2E testing error: unknown tolerance type '{tolerance_type}', expected one of {list(TOLERANCE_TYPES)}."
        )

    @staticmethod
    def _round_to_significant_digits(value: float, significant_digits: int) -> float:
        """
        Rounds a number to a number of significant digits.

        Parameters
        ----------
        value : float
            The number to round.
        significant_digits : int
            The number of significant digits to keep, at least 1.

        Returns
        -------
        float
            The rounded number. Zero, infinities, and NaN are returned unchanged.
        """
        if value == 0 or not math.isfinite(value):
            return value
        return round(value, significant_digits - int(math.floor(math.log10(abs(value)))) - 1)

    @staticmethod
    def is_significant(changes: dict[str, Any], tolerance: float, tolerance_type: str = TOLERANCE_TYPE_PERCENT) -> bool:
        """
        Determines if a numerical change is significant based on if the change between the
        "old_value" and "new_value" exceeds the specified tolerance.

        Parameters
        ----------
        changes : dict[str, Any]
            A dictionary representing changes with "old_value" and "new_value".
        tolerance : float
            The threshold for considering a difference as significant, interpreted according to ``tolerance_type``.
        tolerance_type : str, optional
            How ``tolerance`` is interpreted, one of ``TOLERANCE_TYPES`` (see ``_exceeds_tolerance``). Defaults to
            ``percent``.

        Returns
        -------
        bool
            ``True`` if the values differ beyond the numerical tolerance or contain a non-numerical or structural
            difference; ``False`` otherwise.

        Notes
        -----
        With the default ``percent`` tolerance type, the comparison is based on the absolute difference between the
        "old_value" and "new_value", relative to the "old_value". If the "old_value" is zero, a fallback reference
        value of 1 is used to ensure the tolerance comparison remains meaningful.
        """
        if not (isinstance(changes, dict) and "old_value" in changes and "new_value" in changes):
            return True

        old_value = changes["old_value"]
        new_value = changes["new_value"]

        if old_value == new_value:
            return False

        if isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)):
            return E2ETestResultsHandler._exceeds_tolerance(old_value, new_value, tolerance, tolerance_type)

        if isinstance(old_value, dict) and isinstance(new_value, dict):
            for key in old_value.keys() | new_value.keys():
                if key not in old_value or key not in new_value:
                    return True

                nested_change = {
                    "old_value": old_value[key],
                    "new_value": new_value[key],
                }

                if E2ETestResultsHandler.is_significant(nested_change, tolerance, tolerance_type):
                    return True

            return False

        return True

    @staticmethod
    def filter_nested(
        values_changed: dict[str, dict[str, float | str]],
        tolerance: float,
        tolerance_type: str = TOLERANCE_TYPE_PERCENT,
        variable_tolerances: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        """
        Recursively filters out insignificant numerical changes from a nested structure.

        Parameters
        ----------
        values_changed : dict[str, dict[str, float | str]]
            The ``values_changed`` section of a ``DeepDiff`` result.
        tolerance : float
            The threshold for considering a difference as significant, interpreted according to ``tolerance_type``.
        tolerance_type : str, optional
            How ``tolerance`` is interpreted, one of ``TOLERANCE_TYPES`` (see ``_exceeds_tolerance``). Defaults to
            ``percent``.
        variable_tolerances : dict[str, dict[str, Any]] | None, optional
            Tolerance overrides keyed by variable name. A change whose ``DeepDiff`` path starts with an overridden
            variable is graded with the override's ``tolerance`` and ``tolerance_type`` instead (see
            ``_resolve_tolerance``). ``None`` (the default) grades every change with the given tolerance.

        Notes
        -----
        This method modifies ``values_changed`` in place.
        """
        keys_to_remove = []
        for key, change in values_changed.items():
            key_tolerance, key_tolerance_type = E2ETestResultsHandler._resolve_tolerance(
                key, tolerance, tolerance_type, variable_tolerances
            )
            if isinstance(change, dict) and "old_value" not in change and "new_value" not in change:
                E2ETestResultsHandler.filter_nested(change, key_tolerance, key_tolerance_type)
                if not change:
                    keys_to_remove.append(key)
            elif not E2ETestResultsHandler.is_significant(change, key_tolerance, key_tolerance_type):
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del values_changed[key]

    @staticmethod
    def filter_insignificant_changes(
        diff_result: dict[str, dict[str, dict[str, float | str]]],
        tolerance: float,
        tolerance_type: str = TOLERANCE_TYPE_PERCENT,
        variable_tolerances: dict[str, dict[str, Any]] | None = None,
    ) -> dict[str, dict[str, dict[str, float | str]]]:
        """
        Removes insignificant changes from a ``DeepDiff`` ``values_changed`` section.

        Parameters
        ----------
        diff_result : dict[str, dict[str, dict[str, float | str]]]
            The ``DeepDiff`` result to filter.
        tolerance : float
            The threshold for considering a difference as significant, interpreted according to ``tolerance_type``.
        tolerance_type : str, optional
            How ``tolerance`` is interpreted, one of ``TOLERANCE_TYPES`` (see ``_exceeds_tolerance``). Defaults to
            ``percent``.
        variable_tolerances : dict[str, dict[str, Any]] | None, optional
            Tolerance overrides keyed by variable name, applied to the changes of the variables they list instead of
            ``tolerance`` (see ``filter_nested``). ``None`` (the default) grades every change with ``tolerance``.

        Returns
        -------
        dict[str, dict[str, dict[str, float | str]]]
            The filtered ``DeepDiff`` result.
        """
        values_changed = diff_result.get("values_changed", {})
        E2ETestResultsHandler.filter_nested(values_changed, tolerance, tolerance_type, variable_tolerances)
        if "values_changed" in diff_result and diff_result["values_changed"] == {}:
            del diff_result["values_changed"]
        return diff_result

    @staticmethod
    def update_expected_test_results(output_dir: Path, output_prefix: str) -> None:
        """
        Compares the actual end-to-end testing results for various RuFaS domains and updates the expected
        results in the appropriate domain filter file if differences are found.

        Parameters
        ----------
        output_dir : Path
            The directory to which the actual results are written to.
        output_prefix : str
            The prefix to give the output file names.

        Notes
        -----
        The input set's must-change variables file is not touched: after an update, the freshly recorded expected
        results already reflect any flagged changes, so it is the user's responsibility to empty the must-change
        list, otherwise the leftover flags will fail the next comparison run.
        """
        om = OutputManager()
        info_map: dict[str, Any] = {
            "class": E2ETestResultsHandler.__name__,
            "function": E2ETestResultsHandler.update_expected_test_results.__name__,
        }
        test_result_path_sets = E2ETestResultsHandler._get_test_result_paths(output_prefix)
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

                minified_actual_results = Utility.make_serializable(
                    actual_results, max_depth=om.JSON_OUTPUT_MAX_RECURSIVE_DEPTH
                )
                expected_results["expected_results"] = minified_actual_results
                expected_results["expected_results_last_updated"] = Utility.get_timestamp(include_millis=False)
                E2ETestResultsHandler._write_formatted_json(expected_results_path, expected_results)
            except (IOError, json.JSONDecodeError) as e:
                error_message = (
                    f"Failed to update expected results for {path_set.domain} domain. Error: {str(e)}."
                    " Restoring backup."
                )
                om.add_error(
                    "End-to-end testing expected results update failure.",
                    error_message,
                    info_map,
                )
                shutil.move(backup_path, path_set.expected_results_path)
                raise
            finally:
                if backup_path.exists():
                    backup_path.unlink()

    @staticmethod
    def _get_matching_path(dir_path: Path, path_set: ResultPathType) -> Path | None:
        """
        Returns the path that matches the ``path_set`` actual results path.

        Parameters
        ----------
        dir_path : Path
            The path to the directory.
        path_set : ResultPathType
            ``ResultPathType`` object containing the domain, expected results path, actual results path, and tolerance.

        Returns
        -------
        Path | None
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
    def _check_expected_results_file_keys(data: dict[str, Any]) -> None:
        """
        Checks that the content of an expected results file has every key in ``ORDERED_EXPECTED_RESULTS_FILE_KEYS``.

        Parameters
        ----------
        data : dict[str, Any]
            The content of an expected results file.

        Raises
        ------
        ValueError
            If the data is missing required keys.
        """
        missing_keys = [key for key in ORDERED_EXPECTED_RESULTS_FILE_KEYS if key not in data]
        if missing_keys:
            om = OutputManager()
            om.add_error(
                "End-to-end testing expected results update failure.",
                f"Expected results file missing required keys in data: {missing_keys}",
                {
                    "class": E2ETestResultsHandler.__name__,
                    "function": E2ETestResultsHandler._check_expected_results_file_keys.__name__,
                },
            )
            raise ValueError(f"E2E testing error: Missing required keys in data for JSON file: {missing_keys}")

    @staticmethod
    def _write_formatted_json(file_path: Path, data: dict[str, str]) -> None:
        """
        Writes a JSON file with custom serialization settings for the ``expected_results`` field.

        Parameters
        ----------
        file_path : Path
            The path to the JSON file.
        data : dict[str, str]
            The data to write to the JSON file.

        Raises
        ------
        ValueError
            If the input data is missing required keys.
        """
        E2ETestResultsHandler._check_expected_results_file_keys(data)
        key_order = ORDERED_EXPECTED_RESULTS_FILE_KEYS
        ordered_data = {key: data[key] for key in key_order}
        compact_expected_results = json.dumps(ordered_data["expected_results"], separators=(",", ":"))
        ordered_data["expected_results"] = "__EXPECTED_RESULTS_PLACEHOLDER__"

        json_string = json.dumps(ordered_data, indent=4)
        json_string = json_string.replace('"__EXPECTED_RESULTS_PLACEHOLDER__"', compact_expected_results)
        invalid_prefix = "// WARNING: This is an autogenerated file. Remove this line for valid JSON.\n"
        json_string = invalid_prefix + json_string
        with open(file_path, "w") as file:
            file.write(json_string)

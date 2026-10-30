from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np

from RUFAS.output_manager import LogVerbosity
from RUFAS.post_processing.file_manager import FileManager
from RUFAS.post_processing.graph_generator import GraphGenerator
from RUFAS.post_processing.output_config_validator import OutputConfigValidator
from RUFAS.post_processing.pool_manager import PoolManager
from RUFAS.post_processing.report_generator import ReportGenerator, ReportGeneratorConfig
from RUFAS.post_processing.rufas_logger import configure_logging, get_log_level, get_logger, log
from RUFAS.post_processing.shared_data_types import POOL_ELEMENT_TYPE
from RUFAS.rufas_time import RufasTime
from RUFAS.util import Utility

NON_FILTER_FILE_SUFFIXES = ("must_change_variables.json", "accepted_ranges.json")


class OutputManager:
    """
    Output manager for RuFaS simulation results. Works by collecting variables,
    logs, warnings, and errors into separate pools, and populates requested
    output channels from the pools once the simulation is done.
    """

    __instance: OutputManager | None = None

    def __new__(cls) -> OutputManager:
        if not hasattr(cls, "instance"):
            cls.instance = super(OutputManager, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        if OutputManager.__instance is None:
            OutputManager.__instance = self
            self.__metadata_prefix: str = ""
            self.is_end_to_end_testing_run: bool = False
            self.is_first_post_processing: bool = True
            self._exclude_info_maps_flag: bool = False
            self.__supported_filter_types_prefixes: dict[str, str] = {
                "csv": "csv_",
                "graph": "graph_",
                "json": "json_",
                "report": "report_",
            }
            self.__end_to_end_testing_filter_prefixes: dict[str, str] = {
                "json": "e2e_json_",
                "comparison": "e2e_comparison_",
            }
            self.time: RufasTime | None = None
            self.file_manager = FileManager(self.__metadata_prefix, self._filter_prefixes)
            self.pool_manager = PoolManager(self.file_manager)
            self.output_config_validator = OutputConfigValidator()
            self._logger = get_logger(self.__class__.__name__)

    @property
    def _filter_prefixes(self) -> dict[str, str]:
        """Returns the appropriate set of acceptable filter prefixes."""
        if self.is_end_to_end_testing_run:
            return self.__end_to_end_testing_filter_prefixes
        else:
            return self.__supported_filter_types_prefixes

    def _info_map(self, function_name: str, **extra: Any) -> dict[str, Any]:
        """
        Builds the info map attached to logs, warnings, and errors emitted by ``OutputManager``.

        Parameters
        ----------
        function_name : str
            The name of the function emitting the log.
        **extra : Any
            Additional context to include in the info map.

        Returns
        -------
        dict[str, Any]
            The info map with the class, function, and ``metadata_prefix`` of the log, plus ``extra``.
        """
        return {
            "class": self.__class__.__name__,
            "function": function_name,
            "metadata_prefix": self.__metadata_prefix,
        } | extra

    def run_startup_sequence(
        self,
        verbosity: LogVerbosity,
        exclude_info_maps: bool,
        output_directory: Path,
        clear_output_directory: bool,
        chunkification: bool,
        max_memory_usage_percent: int,
        max_memory_usage: int,
        save_chunk_threshold_call_count: int,
        variables_file_path: Path,
        output_prefix: str,
        task_id: str,
        is_end_to_end_testing_run: bool,
    ) -> None:
        """
        Performs setup tasks required before running the ``OutputManager``.

        Parameters
        ----------
        verbosity : LogVerbosity
            Log verbosity level for the run, applied to the console output of the RuFaS logger.
        exclude_info_maps : bool
            Whether to exclude ``info_map`` from output.
        output_directory : Path
            Directory where output files will be written.
        clear_output_directory : bool
            Whether to clear existing files from the output directory before running.
        chunkification : bool
            Whether to enable pool overflow control via chunkification.
        max_memory_usage_percent : int
            Maximum memory usage as a percentage before triggering a pool flush.
        max_memory_usage : int
            Maximum memory usage in bytes before triggering a pool flush.
        save_chunk_threshold_call_count : int
            Number of calls between chunk save threshold checks.
        variables_file_path : Path
            Path to the variables file, used when clearing the output directory.
        output_prefix : str
            Prefix applied to all generated output file names.
        task_id : str
            Identifier of the task being started.
        is_end_to_end_testing_run : bool
            Whether the current run is an end-to-end testing run.
        """
        self.set_metadata_prefix(output_prefix)
        configure_logging(
            log_directory=output_directory,
            log_level=get_log_level(verbosity),
            output_prefix=output_prefix,
            metadata_prefix=output_prefix,
        )
        self.add_log(
            "start_task",
            f"Starting task: {task_id} ({output_prefix})",
            self._info_map(self.run_startup_sequence.__name__),
        )
        self.pool_manager.flush_pools()
        self.set_exclude_info_maps_flag(exclude_info_maps)
        self.is_end_to_end_testing_run = is_end_to_end_testing_run
        self.file_manager.supported_filter_types_prefixes = self._filter_prefixes
        self.file_manager.create_directory(output_directory)
        if clear_output_directory:
            self.file_manager.clear_output_dir(variables_file_path, output_directory)

        if chunkification:
            self.pool_manager.setup_pool_overflow_control(
                output_directory, max_memory_usage_percent, max_memory_usage, save_chunk_threshold_call_count
            )

    def set_metadata_prefix(self, metadata_prefix: str) -> None:
        """Sets the metadata_prefix attribute."""
        self.__metadata_prefix = metadata_prefix
        self.file_manager.metadata_prefix = metadata_prefix

    def set_exclude_info_maps_flag(self, exclude_info_maps: bool) -> None:
        """
        Sets the ``exclude_info_maps`` flag to the given value.
        Parameters
        ----------
        exclude_info_maps : bool
            The value to set the ``exclude_info_maps`` flag to.
        """

        self._exclude_info_maps_flag = exclude_info_maps

    def save_results(
        self,
        filters_dir_path: Path,
        exclude_info_maps: bool,
        produce_graphics: bool,
        report_dir: Path,
        graphics_dir: Path,
        csv_dir: Path,
        json_dir: Path,
    ) -> None:
        """
        Parses the filter files in the given directory and saves the results to the given path.

        Parameters
        ----------
        filters_dir_path : Path
            Path of the directory containing the files containing the keys for filtering.
        exclude_info_maps : bool
            Flag for whether the user wants to include ``info_maps`` data in their result files.
        produce_graphics: bool
            Flag for whether the user wants to produce graphs at after the simulation.
        report_dir : Path
            The directory for saving reports to.
        graphics_dir : Path
            The directory for saving graphics.
        csv_dir : Path
            The directory for saving CSVs.
        json_dir : Path
            The directory for saving JSONs containing filtered simulation output.

        Notes
        -----
        The filter files can be used to generate different output formats such as JSON, CSV, and graphical output.
        """
        info_map = self._info_map(self.save_results.__name__)
        self.add_log("exclude_info_maps", f"exclude_info_maps flag set to {exclude_info_maps}", info_map)
        list_of_filter_files = self._list_filter_files_in_dir(filters_dir_path)
        report_generator = ReportGenerator(
            ReportGeneratorConfig(metadata_prefix=self.__metadata_prefix, time=self.time)
        )
        if self.pool_manager.chunkification:
            self.pool_manager._save_current_variable_pool()
            self.pool_manager.load_saved_pools()
        for filter_file in list_of_filter_files:
            input_path = filters_dir_path / filter_file
            filter_contents, direction = self.file_manager._load_filter_file_content(input_path)
            is_report = filter_file.startswith(self.__supported_filter_types_prefixes["report"])
            if is_report:
                self.add_log(
                    "init_report_generation",
                    f"Generating report for file: {filter_file}",
                    info_map | {"filter file": filter_file},
                )
            cross_ref_reports: list[str] = []
            limited_significant_digits_reports: list[str] = []
            for filter_content in filter_contents:
                if not self._is_valid_filter_content(filter_content, filter_file):
                    continue

                filtered_pool: dict[str, POOL_ELEMENT_TYPE] = (
                    self.filter_variables_pool(filter_content) if "filters" in filter_content else {}
                )
                if exclude_info_maps:
                    filtered_pool = self._exclude_info_maps(filtered_pool)

                if is_report:
                    report_name = str(filter_content.get("name", input_path.stem))
                    self._generate_report(
                        report_generator, filter_content, filtered_pool, graphics_dir, produce_graphics
                    )
                    self._track_report_options(
                        report_name, filter_content, cross_ref_reports, limited_significant_digits_reports
                    )
                else:
                    self._route_save_functions(
                        filter_file,
                        filtered_pool,
                        produce_graphics,
                        filter_content,
                        json_dir,
                        graphics_dir,
                        csv_dir,
                        direction,
                    )
            if report_generator.reports:
                self._save_reports(
                    report_generator,
                    report_dir,
                    filter_file,
                    direction,
                    cross_ref_reports,
                    limited_significant_digits_reports,
                )

    def _is_valid_filter_content(self, filter_content: Any, filter_file: str) -> bool:
        """
        Checks that a single filter content entry can be processed.

        Parameters
        ----------
        filter_content : Any
            A single entry loaded from a filter file.
        filter_file : str
            The name of the filter file the entry was loaded from.

        Returns
        -------
        bool
            ``True`` if the entry is a dictionary with a ``filters`` or ``cross_references`` entry, ``False``
            otherwise.
        """
        if isinstance(filter_content, dict) and ("filters" in filter_content or "cross_references" in filter_content):
            return True
        filter_name = filter_content.get("name") if isinstance(filter_content, dict) else None
        self.add_error(
            "Parsing error",
            f"Could not parse {filter_name=} in {filter_file=}, it has to have JSON blobs and have `filters` entry. "
            "The `filters` can only be skipped if `cross_references` entry is present and the purpose is to "
            "generate a derived report.",
            self._info_map(self._is_valid_filter_content.__name__, filter_file=filter_file),
        )
        return False

    def _generate_report(
        self,
        report_generator: ReportGenerator,
        filter_content: dict[str, Any],
        filtered_pool: dict[str, POOL_ELEMENT_TYPE],
        graphics_dir: Path,
        produce_graphics: bool,
    ) -> None:
        """
        Generates a report from a single report filter content entry.

        Parameters
        ----------
        report_generator : ReportGenerator
            The report generator collecting the reports for the current report filter file.
        filter_content : dict[str, Any]
            The report filter content. If it contains ``graph_details``, the graphics settings of the current run are
            added to it so that the report can be graphed.
        filtered_pool : dict[str, POOL_ELEMENT_TYPE]
            The pool of filtered data to generate the report from.
        graphics_dir : Path
            The directory for saving graphics.
        produce_graphics : bool
            Flag for whether the user wants to produce graphs.
        """
        if filter_content.get("graph_details"):
            filter_content["graph_details"]["graphics_dir"] = graphics_dir
            filter_content["graph_details"]["produce_graphics"] = produce_graphics
            filter_content["graph_details"]["metadata_prefix"] = self.__metadata_prefix
            self.file_manager.create_directory(graphics_dir)
        report_generator.generate_report(filter_content, filtered_pool)

    def _track_report_options(
        self,
        report_name: str,
        filter_content: dict[str, Any],
        cross_ref_reports: list[str],
        limited_significant_digits_reports: list[str],
    ) -> None:
        """
        Records whether a report uses cross references or limits data significant digits.

        Parameters
        ----------
        report_name : str
            The name of the report.
        filter_content : dict[str, Any]
            The report filter content.
        cross_ref_reports : list[str]
            Names of the reports that use cross references, appended to in place.
        limited_significant_digits_reports : list[str]
            Names of the reports that limit data significant digits, appended to in place.
        """
        if "cross_references" in filter_content:
            cross_ref_reports.append(report_name)
        if "data_significant_digits" in filter_content:
            limited_significant_digits_reports.append(report_name)

    def _save_reports(
        self,
        report_generator: ReportGenerator,
        report_dir: Path,
        filter_file: str,
        direction: str | None,
        cross_ref_reports: list[str],
        limited_significant_digits_reports: list[str],
    ) -> None:
        """
        Saves the reports generated from a single report filter file to CSV and clears them from the generator.

        Parameters
        ----------
        report_generator : ReportGenerator
            The report generator holding the generated reports.
        report_dir : Path
            The directory for saving reports to.
        filter_file : str
            The name of the report filter file the reports were generated from.
        direction : str | None
            The direction of the CSV file, either portrait or landscape.
        cross_ref_reports : list[str]
            Names of the reports in the filter file that use cross references.
        limited_significant_digits_reports : list[str]
            Names of the reports in the filter file that limit data significant digits.
        """
        if cross_ref_reports and limited_significant_digits_reports:
            significant_digits_limited_reports = ", ".join(
                f"'{report}'" for report in limited_significant_digits_reports
            )
            cross_referenced_reports = ", ".join(f"'{report}'" for report in cross_ref_reports)
            self.add_warning(
                "Report Generation Warning",
                "Reports generated have both cross references and data significant digits. "
                f"Significant digits were limited for the following reports: {significant_digits_limited_reports}. "
                f"Results may be affected for the following cross-referenced reports: {cross_referenced_reports}.",
                self._info_map(self._save_reports.__name__, filter_file=filter_file),
            )
        self.file_manager.create_directory(report_dir)
        report_file_path = report_dir / self.file_manager.generate_file_name(f"{filter_file}", "csv")
        self.file_manager._dict_to_file_csv(report_generator.reports, report_file_path, direction)
        report_generator.clear_reports()

    def _route_save_functions(
        self,
        filter_file: str,
        filtered_pool: dict[str, POOL_ELEMENT_TYPE],
        produce_graphics: bool,
        filter_content: dict[str, Any],
        json_dir: Path,
        graphics_dir: Path,
        csv_dir: Path,
        direction: str | None,
    ) -> None:
        """
        Checks the prefix of the ``filter_file`` to determine the format for saving. It then delegates the
        saving process to the corresponding function to handle specific formats such as JSON, CSV, or graphical output.

        Parameters
        ----------
        filter_file : str
            The name of the filter file being processed.
        filtered_pool : dict[str, POOL_ELEMENT_TYPE]
            The pool of filtered data to be saved.
        produce_graphics : bool
            Flag for whether the user wants to produce graphs.
        filter_content : dict[str, Any]
            The filter content used to produce ``filtered_pool``.
        json_dir : Path
            The directory for saving JSONs.
        graphics_dir : Path
            The directory for saving graphics.
        csv_dir : Path
            The directory for saving CSVs.
        direction : str | None
            The direction of the CSV file, either portrait or landscape.
        """
        info_map = self._info_map(self._route_save_functions.__name__, filter_file=filter_file)
        if "data_significant_digits" in filter_content:
            significant_digits = int(filter_content["data_significant_digits"])
            filtered_pool = {
                key: (
                    Utility.round_numeric_values_in_dict(value, significant_digits)
                    if isinstance(value, dict)
                    else value
                )
                for key, value in filtered_pool.items()
            }
            self.add_log("Rounding Values", f"Rounded values to {significant_digits} significant digits", info_map)

        if self._has_filter_prefix(filter_file, "json") and self.is_first_post_processing:
            self.file_manager.create_directory(json_dir)
            self.file_manager._save_to_json(filter_file, json_dir, filtered_pool, filter_content)
            return
        if self._has_filter_prefix(filter_file, "csv"):
            self.file_manager.create_directory(csv_dir)
            variable_csv_file_path = csv_dir / self.file_manager.generate_file_name(
                f"saved_variables_{filter_file}", "csv"
            )
            self.file_manager._dict_to_file_csv(filtered_pool, variable_csv_file_path, direction)
            return
        if self._has_filter_prefix(filter_file, "graph"):
            self.file_manager.create_directory(graphics_dir)
            self._generate_graph(filter_file, filtered_pool, filter_content, graphics_dir, produce_graphics)
            return
        if self._has_filter_prefix(filter_file, "comparison") and not self.is_first_post_processing:
            self.file_manager.create_directory(json_dir)
            self.file_manager._save_to_json(filter_file, json_dir, filtered_pool, filter_content)

    def _generate_graph(
        self,
        filter_file: str,
        filtered_pool: dict[str, POOL_ELEMENT_TYPE],
        filter_content: dict[str, Any],
        graphics_dir: Path,
        produce_graphics: bool,
    ) -> None:
        """
        Generates a graph from a graph filter using ``GraphGenerator``.

        Parameters
        ----------
        filter_file : str
            The name of the graph filter file being processed.
        filtered_pool : dict[str, POOL_ELEMENT_TYPE]
            The pool of filtered data to graph.
        filter_content : dict[str, Any]
            The graph filter content.
        graphics_dir : Path
            The directory for saving graphics.
        produce_graphics : bool
            Flag for whether the user wants to produce graphs.
        """
        info_map = self._info_map(self._generate_graph.__name__, filter_file=filter_file)
        if not produce_graphics:
            self.add_warning("No Graphics", f"Graphic generation is disabled, skipping {filter_file=}", info_map)
            return
        if self.time is None:
            self.add_error(
                "graph generation exception",
                f"Cannot graph {filter_file=} because OutputManager's 'time' attribute is not initialized.",
                info_map,
            )
            return
        try:
            graph_generator = GraphGenerator(self.time, self.__metadata_prefix)
            graph_generator.generate_graph(filtered_pool, filter_content, filter_file, graphics_dir, produce_graphics)
        except Exception as e:
            self.add_error("graph generation exception", str(e), info_map)

    def _has_filter_prefix(self, filter_file: str, filter_type: str) -> bool:
        """
        Checks whether a filter file name starts with the prefix of the given filter type.

        Parameters
        ----------
        filter_file : str
            The name of the filter file.
        filter_type : str
            The filter type key, e.g. ``"json"``, ``"csv"``, ``"graph"``, or ``"comparison"``.

        Returns
        -------
        bool
            ``True`` if the filter type is supported for the current run and ``filter_file`` starts with its prefix.
        """
        prefix = self._filter_prefixes.get(filter_type)
        return prefix is not None and filter_file.startswith(prefix)

    def dump_all_nondata_pools(
        self,
        path: Path,
        exclude_info_maps: bool,
        format_option: str,
    ) -> None:
        """
        Dumps all non-data pools to timestamped files in the given directory.

        Writes variable names and contexts and variable usage counts. Logs, warnings, and errors are handled by the
        RuFaS logger.

        Parameters
        ----------
        path : Path
            Directory path where all output files will be written.
        exclude_info_maps : bool
            Whether to exclude ``info_map`` from the variable names and contexts output.
        format_option : str
            Format option passed to ``PoolManager.dump_variable_names_and_contexts()``.
        """
        # TODO Save logs, warnings, and errors once log pool saving is set up (#3343).
        self.file_manager.create_directory(path)
        self.pool_manager.dump_variable_names_and_contexts(path, exclude_info_maps, format_option)
        self.pool_manager.report_variables_usage_counts(path)

    def summarize_e2e_test_results(
        self,
        json_output_directory: Path,
        output_prefixes: list[str],
        e2e_random_seeds: dict[str, list[int]],
        failed_e2e_groups: list[str] | None = None,
    ) -> None:
        """
        Summarizes the end-to-end test results by gathering the results from all the e2e tests and prepares them to be
        printed out to the console.
        This method is intended to be called at the end of an end-to-end testing run.

        Parameters
        ----------
        json_output_directory : Path
            The directory where the JSON output files are located.
        output_prefixes : list[str]
            A list of output prefixes to look for in the filenames.
        e2e_random_seeds : dict[str, list[int]]
            The random seeds used for each e2e test group.
        failed_e2e_groups : list[str] | None, default None
            The output prefixes of the tasks that failed. They are summarized as not run, and any results files found
            for them are ignored because they were left by an earlier run.
        """
        info_map = self._info_map(self.summarize_e2e_test_results.__name__)
        failed_e2e_groups = failed_e2e_groups or []
        self.add_log(
            "Attempting to open e2e test results directory",
            "Opening e2e test results directory to read results files",
            info_map,
        )
        module_headers: list[str] = ["Animal", "CropAndSoil", "Manure", "Feed"]
        e2e_results_summary: dict[str, dict[str, bool | str]] = {
            prefix: {
                header: "not run (task failed)" if prefix in failed_e2e_groups else "n/a" for header in module_headers
            }
            for prefix in output_prefixes
        }
        for filename in os.listdir(json_output_directory):
            if "comparison" not in filename.lower() or not filename.endswith(".json"):
                continue
            file_path = json_output_directory / filename
            try:
                with open(file_path, "r") as file:
                    data: dict[str, Any] = json.load(file)
            except Exception as exc:
                self.add_error("File path invalid.", f"Failed to read {file_path}: {exc}", info_map)
                continue

            matched_prefix = next((prefix for prefix in output_prefixes if prefix.lower() in filename.lower()), None)
            if matched_prefix is None:
                self.add_error(
                    "Invalid e2e output prefix", f"No matching output_prefix found in filename: {filename}", info_map
                )
                continue
            if matched_prefix in failed_e2e_groups:
                continue

            for key, value in data.items():
                if key == "DISCLAIMER":
                    continue
                module = self.file_manager._normalize_module_header(key)
                e2e_results_summary[matched_prefix][module] = value["values"][0]

        self.add_log(
            "Successfully opened e2e test results directory", "Directory opened and files successfully read", info_map
        )
        self._print_e2e_results_summary(e2e_results_summary, e2e_random_seeds)

    def _print_e2e_results_summary(
        self,
        e2e_results_summary: dict[str, dict[str, bool | str]],
        e2e_random_seeds: dict[str, list[int]],
    ) -> None:
        """
        Prints the end-to-end results summary to the console.

        Parameters
        ----------
        e2e_results_summary : dict[str, dict[str, bool | str]]
            Mapping of output prefix to the result of each module.
        e2e_random_seeds : dict[str, list[int]]
            The random seeds used for each e2e test group.
        """
        sys.stdout.write("\nSummary of e2e results:\n\n")
        for prefix, results in e2e_results_summary.items():
            sys.stdout.write(f"{prefix} results:\n")
            random_seeds = e2e_random_seeds.get(prefix)
            if random_seeds:
                formatted_seeds = ", ".join(str(seed) for seed in random_seeds)
                sys.stdout.write(f"  Results averaged across random seeds: {formatted_seeds}\n")
            for module, result in results.items():
                result = "Passing" if result is True else "Failing" if result is False else result
                sys.stdout.write(f"  {module}: {result}\n")
            sys.stdout.write("\n")

    def _exclude_info_maps(self, pool: dict[str, POOL_ELEMENT_TYPE]) -> dict[str, POOL_ELEMENT_TYPE]:
        """
        Returns a copy of the given pool with ``info_maps`` removed from each entry.

        Parameters
        ----------
        pool : dict[str, POOL_ELEMENT_TYPE]
            The pool to copy and strip of ``info_maps``.

        Returns
        -------
        dict[str, POOL_ELEMENT_TYPE]
            Copy of the pool with ``info_maps`` removed from each entry.
        """
        return {
            key: (
                {sub_key: sub_value for sub_key, sub_value in value.items() if sub_key != "info_maps"}
                if isinstance(value, dict)
                else value
            )
            for key, value in pool.items()
        }

    def filter_variables_pool(self, filter_content: dict[str, Any]) -> dict[str, POOL_ELEMENT_TYPE]:
        """
        Returns a filtered ``variables_pool`` based on options specified in ``filter_content``.

        Parameters
        ----------
        filter_content : dict[str, Any]
            A dictionary that contains filtering options.

        Returns
        -------
        dict[str, POOL_ELEMENT_TYPE]
            A filtered ``variables_pool`` based on either inclusion or exclusion.

        Raises
        ------
        RuntimeError
            If ``expand_data`` is ``True`` but the ``time`` attribute has not been
            initialized on the ``OutputManager``.
        """
        filter_name: str = filter_content.get("name", "NO NAME FOUND")
        filter_by_exclusion: bool = filter_content.get("filter_by_exclusion", False)
        info_map = self._info_map(
            self.filter_variables_pool.__name__, filter_name=filter_name, filter_by_exclusion=filter_by_exclusion
        )
        filter_mode = "exclusion" if filter_by_exclusion else "inclusion"
        self.add_log(
            "filtering_log", f"Performing filtering by {filter_mode} per filter's contents. {filter_name=}", info_map
        )

        filtered_pool: dict[str, POOL_ELEMENT_TYPE] = Utility.filter_dictionary(
            dict_to_filter=self.pool_manager._get_flat_variables_pool(),
            filter_patterns=filter_content.get("filters", []),
            filter_by_exclusion=filter_by_exclusion,
        )
        self.add_log(
            "num_filter_pattern_matches",
            f"There were {len(filtered_pool)} matches for filter pattern(s) in {filter_name=}.",
            info_map,
        )

        results = self._parse_filtered_variables(
            filtered_pool,
            filter_content.get("variables"),
            filter_name,
            filter_by_exclusion,
        )

        if filter_content.get("expand_data", False):
            results = self._expand_filtered_data(results, filter_content, filter_name)

        slice_start: int = filter_content.get("slice_start", 0)
        slice_end: int | None = filter_content.get("slice_end", None)
        for key in results.keys():
            if "info_maps" in results[key]:
                results[key]["info_maps"] = results[key]["info_maps"][slice_start:slice_end]
            results[key]["values"] = results[key]["values"][slice_start:slice_end]

        return results

    def _expand_filtered_data(
        self,
        results: dict[str, POOL_ELEMENT_TYPE],
        filter_content: dict[str, Any],
        filter_name: str,
    ) -> dict[str, POOL_ELEMENT_TYPE]:
        """
        Expands filtered data temporally over the simulation length using the fill options in ``filter_content``.

        Parameters
        ----------
        results : dict[str, POOL_ELEMENT_TYPE]
            The filtered and parsed variables to expand.
        filter_content : dict[str, Any]
            A dictionary that contains the data expansion options.
        filter_name : str
            Name of the filter used to collect the variables.

        Returns
        -------
        dict[str, POOL_ELEMENT_TYPE]
            The expanded variables, or ``results`` unchanged if the expansion failed.

        Raises
        ------
        RuntimeError
            If the ``time`` attribute has not been initialized on the ``OutputManager``.
        """
        if self.time is None:
            raise RuntimeError("Cannot expand data because OutputManager's 'time' attribute is not initialized.")
        try:
            results, expansion_logs = Utility.expand_data_temporally(
                results,
                simulation_length=self.time.simulation_length_days,
                fill_value=filter_content.get("fill_value", np.nan),
                use_fill_value_before_start=filter_content.get("use_fill_value_before_start", True),
                use_fill_value_in_gaps=filter_content.get("use_fill_value_in_gaps", True),
                use_fill_value_at_end=filter_content.get("use_fill_value_at_end", True),
                expand_data_to_observed_range=filter_content.get("expand_data_to_observed_range", False),
            )
            self._log_event_pool(expansion_logs)
        except (TypeError, ValueError) as e:
            self.add_error(
                f"Error {e} raised when padding data",
                f"Unable to pad data for variables gathered for {filter_name=}.",
                self._info_map(self._expand_filtered_data.__name__, filter_name=filter_name),
            )
        return results

    def _log_event_pool(self, event_pool: list[dict[str, Any]]) -> None:
        """
        Emits legacy-format log, warning, and error events through the RuFaS logger.

        Parameters
        ----------
        event_pool : list[dict[str, Any]]
            Events whose first key is one of ``log``, ``warning``, or ``error`` (the event name), with accompanying
            ``message`` and ``info_map`` entries.
        """
        levels = {"error": logging.ERROR, "warning": logging.WARNING, "log": logging.INFO}
        for event in event_pool:
            event_type = next((key for key in levels if key in event), None)
            if event_type is None:
                self.add_warning(
                    "Unsupported event key for output manager",
                    f"Valid event keys are {list(levels)}. Given event contains the keys {list(event.keys())}",
                    self._info_map(self._log_event_pool.__name__),
                )
                continue
            log(
                logger=self._logger,
                level=levels[event_type],
                name=str(event[event_type]),
                message=str(event.get("message", "")),
                info_map=event.get("info_map"),
            )

    def _parse_filtered_variables(
        self,
        filtered_pool: dict[str, POOL_ELEMENT_TYPE],
        selected_variables: list[str] | None,
        filter_name: str,
        filter_by_exclusion: bool,
    ) -> dict[str, POOL_ELEMENT_TYPE]:
        """
        Unpacks and counts variables that have been filtered out of the ``variables_pool``.

        Parameters
        ----------
        filtered_pool : dict[str, POOL_ELEMENT_TYPE]
            Variables that have been filtered out of the ``variables_pool``.
        selected_variables : list[str] | None
            List of key names to select or exclude from variables containing dictionaries.
        filter_name : str
            Name of the filter used to collect variables for the filtered pool.
        filter_by_exclusion : bool
            Whether keys in dictionaries should be filtered by exclusion.

        Returns
        -------
        dict[str, POOL_ELEMENT_TYPE]
            Dictionary containing data from the filtered pool of data, with data from within dictionaries unpacked and
            separated.
        """
        usage_counter = self.pool_manager._variables_usage_counter
        results: dict[str, POOL_ELEMENT_TYPE] = {}
        for key, entry in filtered_pool.items():
            info_maps: list[dict[str, Any]] = entry.get("info_maps", [])
            data: list[Any] = entry["values"]
            is_data_in_dict: bool = all(isinstance(element, dict) for element in data)
            if selected_variables is None or not is_data_in_dict:
                results[key] = ({"info_maps": info_maps} if info_maps else {}) | {"values": data}
                usage_counter.update([key])
                continue

            if not isinstance(selected_variables, list):
                self.add_error(
                    "Unpacking Pool Error",
                    f"Unable to unpack {key=} in the data pool, need a valid `variables` entry for this entry."
                    f"{is_data_in_dict=}, {selected_variables=}, see Wiki for proper setup details.",
                    self._info_map(
                        self._parse_filtered_variables.__name__,
                        filter_name=filter_name,
                        filter_by_exclusion=filter_by_exclusion,
                    ),
                )
            temp_data = Utility.convert_list_of_dicts_to_dict_of_lists(data)
            filtered_data = Utility.filter_dictionary(temp_data, selected_variables, filter_by_exclusion)
            for filtered_key, filtered_value in filtered_data.items():
                combined_key = f"{key}.{filtered_key}"
                if combined_key in results:
                    results[combined_key].get("info_maps", []).extend(info_maps)
                    results[combined_key]["values"].extend(filtered_value)
                else:
                    results[combined_key] = ({"info_maps": info_maps} if info_maps else {}) | {"values": filtered_value}
                usage_counter.update([combined_key])
        return results

    def _list_filter_files_in_dir(self, dir_path: Path) -> list[str]:
        """
        Returns the list of supported filter files in the given path.

        Parameters
        ----------
        dir_path : Path
            The directory to search for filter files.

        Returns
        -------
        list[str]
            Names of the ``.txt`` and ``.json`` files in ``dir_path`` whose prefix is supported for the current run.

        Raises
        ------
        NotADirectoryError
            If ``dir_path`` is not a valid directory.
        """
        info_map = self._info_map(self._list_filter_files_in_dir.__name__)
        self.add_log("search_path_for_filenames_try", f"Attempting to search in {dir_path}.", info_map)
        if not dir_path.is_dir():
            raise NotADirectoryError(f"The specified path {dir_path} must be a valid directory")

        supported_prefixes = tuple(self._filter_prefixes.values())
        filter_files = []
        for filename in os.listdir(dir_path):
            if filename.endswith(NON_FILTER_FILE_SUFFIXES) or not filename.endswith((".txt", ".json")):
                continue
            if not filename.startswith(supported_prefixes):
                self.add_warning(
                    "invalid filter file prefix", f"{filename} prefix is not in {list(supported_prefixes)}", info_map
                )
                continue
            filter_files.append(filename)
        self.add_log(
            "search_path_for_filenames_success",
            f"Successfully searched in {dir_path} and found {len(filter_files)} filter files.",
            info_map,
        )
        return filter_files

    def add_log(
        self,
        name: str,
        message: str,
        info_map: dict[str, Any],
    ) -> None:
        log(
            logger=self._logger,
            level=logging.INFO,
            name=name,
            message=message,
            info_map=info_map,
        )

    def add_warning(
        self,
        name: str,
        message: str,
        info_map: dict[str, Any],
    ) -> None:
        log(
            logger=self._logger,
            level=logging.WARNING,
            name=name,
            message=message,
            info_map=info_map,
        )

    def add_error(
        self,
        name: str,
        message: str,
        info_map: dict[str, Any],
    ) -> None:
        log(
            logger=self._logger,
            level=logging.ERROR,
            name=name,
            message=message,
            info_map=info_map,
        )

from __future__ import annotations

import json
import os
import sys
from copy import deepcopy
from enum import Enum
from functools import partial
from pathlib import Path
from typing import Any, Sequence, TextIO, Union, Callable

from collections import Counter
import collections
import numpy as np
import pandas as pd
import psutil

from RUFAS.general_constants import GeneralConstants
from RUFAS.graph_generator import GraphGenerator
from RUFAS.report_generator import ReportGenerator
from RUFAS.units import MeasurementUnits
from RUFAS.user_constants import UserConstants
from RUFAS.util import Utility

DISCLAIMER_MESSAGE = "Under construction, use the results with caution."


class LogVerbosity(Enum):
    """
    The different types of logs printed by Output Manager. Set by the `verbose` gnu arg in main.py.

    Attributes
    ----------
    NONE : str
        Selecting NONE will tell OutputManager not to print out anything during a simulation.
    CREDITS : str
        Selecting CREDITS will tell OutputManager to print out the credits.
    ERRORS : str
        Selecting ERRORS will tell OutputManager to print out all credits and errors added during a simulation.
    WARNINGS : str
        Selecting WARNINGS will tell OutputManager to print out the credits as well as warnings and errors added during
        a simulation.
    LOGS : str
        Selecting LOGS will tell OutputManager to print out the credits as well as logs, warnings, and errors added
        during a simulation.

    Notes
    -----
    CREDITS is the default setting.

    """

    NONE = "none"
    CREDITS = "credits"
    ERRORS = "errors"
    WARNINGS = "warnings"
    LOGS = "logs"

    def __le__(self, other: "LogVerbosity") -> bool:
        order = {
            LogVerbosity.NONE: 0,
            LogVerbosity.CREDITS: 1,
            LogVerbosity.ERRORS: 2,
            LogVerbosity.WARNINGS: 3,
            LogVerbosity.LOGS: 4,
        }

        if other == LogVerbosity.NONE and self != LogVerbosity.NONE:
            return False

        return order[self] <= order[other]

    def __str__(self) -> str:
        if self.value == "none":
            return "NONE"
        return self.value[:-1].upper()


class OriginLabel(Enum):
    """
    An enumeration representing the different labels for data origins when generating json output files.

    Attributes
    ----------
    TRUE_AND_REPORT_ORIGINS : str
        Indicates that both the true origin and report origin should be included.
    TRUE_ORIGIN : str
        Indicates that only the true origin should be included.
    REPORT_ORIGIN : str
        Indicates that only the report origin should be included.
    NONE : str
        Indicates that no origin information should be included.

    """

    TRUE_AND_REPORT_ORIGINS = "true and report origins"
    TRUE_ORIGIN = "true origin"
    REPORT_ORIGIN = "report origin"
    NONE = "none"


class OutputManager(object):
    """
    Output manager for RuFaS simulation results. Works by collecting variables,
    logs, warnings, and errors into separate pools, and populates requested
    output channels from the pools once the simulation is done.

    OutputManager is singleton, i.e., only one instance of it can exist. After
    the first instance is created, future calls to the constructor method
    returns the first instance. Also, the initializer method only works once.

    Class Attributes
    ----------------
    pool_element_type : dict[str, list[Any]]
        Type alias for the pool elements
    JSON_OUTPUT_MAX_RECURSIVE_DEPTH : int
        Maximum depth for recursive serialization in JSON output files (default: 4)

    Attributes
    ----------
    variables_pool : dict[str, dict[str, list[dict[str, Any]]]
        Contains variables reported to the output manager
    warnings_pool : dict[str, dict[str, list[dict[str, Any]]]
        Contains warnings reported to the output manager
    errors_pool : dict[str, dict[str, list[dict[str, Any]]]
        Contains errors reported to the output manager
    logs_pool : dict[str, dict[str, list[dict[str, Any]]]
        Contains logs reported to the output manager
    time : RufasTime
        A RufasTime object used to track the simulation time
    _exclude_info_maps_flag : bool
        Set to True to exclude info_maps when adding variables to the variables_pool
    _variables_usage_counter : Counter[str]
        A Counter object used to keep track of the number of times a variables in the variables_pool is used.
    is_end_to_end_testing_run : bool, default False
        Indicates if end-to-end testing is being run.
    is_first_post_processing : bool, default True
        True if post-processing (i.e. filtering and saving variables) has not occurred yet. This variable is used during
        end-to-end testing to manage which filters are used during different post-processing runs.
    chunkification : bool
        Set to True to enable chunkification of the output variable pool.
    saved_pool_chunks_num : int
        The number of saved pool chunks.
    saved_pool_chunks_path : Path | None
        The path to the directory where saved pool chunks are stored.
    available_memory : int
        The available memory on the system.
    average_add_variable_call_addition : int, default 118
        The average memory usage increase per call to add_variable.
    add_variable_call : int
        The number of calls to add_variable().
    save_chunk_threshold_call_count : int
        The threshold add_variable_call count for saving pool chunk.
    current_pool_size : int
        The current size of the variables pool.
    maximum_pool_size : float
        The maximum allowed variable pool size.
    """

    __instance = None
    pool_element_type = dict[str, list[Any]]
    JSON_OUTPUT_MAX_RECURSIVE_DEPTH = 4

    def __new__(cls) -> OutputManager:
        if not hasattr(cls, "instance"):
            cls.instance = super(OutputManager, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        if OutputManager.__instance is None:
            OutputManager.__instance = self
            self.variables_pool: dict[str, OutputManager.pool_element_type] = {}
            self.warnings_pool: dict[str, OutputManager.pool_element_type] = {}
            self.errors_pool: dict[str, OutputManager.pool_element_type] = {}
            self.logs_pool: dict[str, OutputManager.pool_element_type] = {}
            self._exclude_info_maps_flag: bool = False
            self.__metadata_prefix: str = ""
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
            self.__log_verbose: LogVerbosity = LogVerbosity.CREDITS

            self.chunkification: bool = False
            self.saved_pool_chunks_num: int = 0
            self.saved_pool_chunks_path: Path | None = None

            self.available_memory: int = 0
            self.average_add_variable_call_addition: int = 118
            self.add_variable_call = 0
            self.save_chunk_threshold_call_count: int = 0
            self.current_pool_size: int = 0
            self.maximum_pool_size: float = np.inf

            self.add_log(
                "init_log",
                "Output Manager instantiated.",
                info_map={
                    "class": self.__class__.__name__,
                    "function": "__init__",
                },
            )
            self.time = None
            self._variables_usage_counter: Counter[str] = collections.Counter()
            self.is_end_to_end_testing_run: bool = False
            self.is_first_post_processing: bool = True

    @property
    def _filter_prefixes(self) -> dict[str, str]:
        """Returns the appropriate set of acceptable filter prefixes."""
        if self.is_end_to_end_testing_run:
            return self.__end_to_end_testing_filter_prefixes
        else:
            return self.__supported_filter_types_prefixes

    def setup_pool_overflow_control(
        self,
        output_dir: Path,
        max_memory_usage_percent: int,
        max_memory_usage: int | None = None,
        save_chunk_threshold_call_count: int | None = None,
    ) -> None:
        """Sets up the mechanism by which chunkification of the output variable pool is controlled.

        Parameters
        ----------
        output_dir : Path
            The path to the output directory where chunks will be saved.
        max_memory_usage_percent : int
            The setting for the maximum output variable pool size as a percentage of the available memory.
        max_memory_usage : int | None, optional
            The setting for the maximum output variable pool size in bytes.
        save_chunk_threshold_call_count : int | None, optional
            The setting for the threshold add_variable_call count for saving pool chunk.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.setup_pool_overflow_control.__name__,
        }
        self.chunkification = True

        self.available_memory = psutil.virtual_memory().available
        available_memory_gb = self.available_memory / GeneralConstants.BYTES_PER_GB

        self.saved_pool_chunks_path = Path.joinpath(
            output_dir, f"saved_pool/{self.__metadata_prefix}_{Utility.get_timestamp(include_millis=True)}"
        )
        self.create_directory(self.saved_pool_chunks_path)

        log_message = (
            f"Created {self.saved_pool_chunks_path} for saved pools during simulation.\n"
            f"Current system available memory: {available_memory_gb:.2f} GB = "
            f"{self.available_memory} Bytes.\n"
        )

        if save_chunk_threshold_call_count is not None and save_chunk_threshold_call_count > 0:
            self.save_chunk_threshold_call_count = save_chunk_threshold_call_count
            log_message += (
                "The threshold add_variable_call count for saving pool chunk is set to "
                f"{self.save_chunk_threshold_call_count}"
            )
        elif max_memory_usage:
            self.maximum_pool_size = max_memory_usage
            log_message += "The maximum output variable pool size is set to " f"{self.maximum_pool_size} Bytes"
        else:
            self.maximum_pool_size = (
                max_memory_usage_percent * GeneralConstants.PERCENTAGE_TO_FRACTION
            ) * self.available_memory
            log_message += "The maximum output variable pool size is set to " f"{self.maximum_pool_size} Bytes"
        self.add_log(
            "Pool Overflow Control Setup",
            log_message,
            info_map,
        )

    def _pool_element_factory(self) -> pool_element_type:
        """Factory for elements added to pools"""
        info_maps: list[dict[str, Any]] = []
        values: list[Any] = []
        return {"info_maps": info_maps, "values": values}

    def _add_to_pool(
        self,
        pool: dict[str, pool_element_type],
        key: str,
        value: Any,
        info_map: dict[str, Any],
        first_info_map_only: bool = False,
    ) -> None:
        """
        Adds value and info map at key in the given pool.

        Parameters
        ----------
        pool : dict[str, dict[str, list[dict[str, Any]]]
            The pool to add the value and info_map to.
        key : str
            The key to add the value and info_map at.
        value : Any
            The value to be added to the pool.
        info_map : dict[str, Any]
            The info map to be added to the pool.
        first_info_map_only : bool, default False
            If true, records only the first info map passed for that variable. If false, records all info maps passed
            for that variable.

        """
        discard_info_map = first_info_map_only

        key_not_exists_in_pool = pool.get(key) is None
        if key_not_exists_in_pool:
            pool[key] = self._pool_element_factory()
            discard_info_map = False

        if not self._exclude_info_maps_flag and not discard_info_map:
            reduced_info_map = {k: v for k, v in info_map.items() if k not in ["class", "function"]}
            pool[key]["info_maps"].append(reduced_info_map)

        if isinstance(value, (int, bool, float, str)):
            pool[key]["values"].append(value)
        else:
            pool[key]["values"].append(deepcopy(value))

    def add_variable(self, name: str, value: Any, info_map: dict[str, Any], first_info_map_only: bool = False) -> None:
        """
        Adds a variable to the pool.

        Parameters
        ----------
        name : str
            The name of the variable
        value : Any
            The value of the variable
        info_map : dict[str, Any]
            Additional args, some are non-optional
        info_map["class"] : str
            The name of the class which called this function
        info_map["function"] : str
            The name of the function which called this function
        info_map["prefix"] : str, optional
            If present, overrides the automated prefix
        info_map["suppress_prefix"] : bool, optional
            If present and True, suppresses the automated prefix generation.
            Has no effect on manual prefix overrides.
        info_map["suffix"] : str, optional
            If present, gets appended to the key
        first_info_map_only : bool, default False
            If true, records only the first info map passed for that variable. If false, records all info maps passed
            for that variable.

        """
        self.add_variable_call += 1
        units = info_map.get("units")
        if units is None:
            raise KeyError(f"'units' was not found in info_map for call to 'add_variable()' for {name}.")
        if isinstance(units, dict) and len(info_map["units"]) != len(value) and value != {}:
            raise KeyError(f"'units' missing in units dict for a variable in {name}.")
        units = self._stringify_units(units)

        key = self._generate_key(name, info_map)
        self._add_to_pool(self.variables_pool, key, value, {**info_map, "units": units}, first_info_map_only)

        if isinstance(value, dict):
            for k, v in value.items():
                self._variables_usage_counter[f"{key}.{k}"] = 0

        if self.chunkification:
            self.current_pool_size += self.average_add_variable_call_addition
            is_save_chunk_threshold_reached = (
                self.save_chunk_threshold_call_count > 0
                and self.add_variable_call % self.save_chunk_threshold_call_count == 0
            )
            is_pool_size_at_maximum_capacity = (
                self.save_chunk_threshold_call_count == 0 and self.current_pool_size >= self.maximum_pool_size
            )
            if is_save_chunk_threshold_reached or is_pool_size_at_maximum_capacity:
                self._save_current_variable_pool()

    def add_variable_bulk(
        self, variables: list[tuple[dict[str, Any], dict[str, Any]]], first_info_map_only: bool = False
    ) -> None:
        """
        Iterate through all variables and call add_variable() on each of them.

        Parameters
        ----------
        variables : list[tuple[dict[str, Any], dict[str, Any]]
            Variables to add in bulk packages in a list of tuples. Each tuple contains a dictionary with the key
            being the variable name and the value being the output value, and its corresponding info map.
        first_info_map_only : bool, default False
            If true, records only the first info_map passed for each variable.
        """
        for variable, info_map in variables:
            name, value = list(variable.items())[0]
            self.add_variable(name, value, info_map, first_info_map_only)

    def _save_current_variable_pool(self) -> None:
        """
        Save the current variable pool into JSON file. Flush the variable pool and reset the pool size.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._save_current_variable_pool.__name__,
        }

        saved_pool_file_name = self.generate_file_name(f"saved_pool_{self.saved_pool_chunks_num}", "json")
        saved_pool_file_path = Path.joinpath(self.saved_pool_chunks_path, saved_pool_file_name)
        self.dict_to_file_json(data_dict=self.variables_pool, path=saved_pool_file_path, minify_output_file=True)
        self.add_log(
            "save_current_variable_pool",
            f"Saved the current variable pool to {saved_pool_file_path}",
            info_map,
        )
        self._set_variables_pool({})
        self.saved_pool_chunks_num += 1

    def _stringify_units(self, units: dict[str, Any] | MeasurementUnits) -> dict[str, Any] | str:
        """
        Recursively validates that units is either a valid MeasurementUnits enum member or a dictionary with
        valid MeasurementUnits enum members (including nested dictionaries). Converts the MeasurementUnits
        enum values to their string representations.

        Parameters
        ----------
        units : dict[str, Any] | str
            Either a string that can be converted to an MeasurementUnits, or a dictionary mapping string keys to either
            MeasurementUnits values or further dictionaries.

        Returns
        -------
        dict[str, Any] | str
            The validated and stringified units.

        Raises
        ------
        TypeError
            If any unit or nested unit does not have the type MeasurementUnits.

        """
        if isinstance(units, dict):
            return {key: self._stringify_units(unit) for key, unit in units.items()}

        if type(units) is not MeasurementUnits:
            self.add_error(
                "invalid_units_type",
                f"The following unit does not have the type MeasurementUnits: {units} (type {type(units)}).",
                info_map={
                    "class": self.__class__.__name__,
                    "function": self._stringify_units.__name__,
                },
            )

            raise TypeError(
                f"The following unit does not have the type MeasurementUnits: {units} (type {type(units)})."
            )

        return str(units)

    def add_log(self, name: str, msg: str, info_map: dict[str, Any]) -> None:
        """
        Adds a log message to the pool of logs.

        Parameters
        ----------
        name : str
            The name of the log
        msg : str
            The log message to be added to the pool
        info_map: dict[str, Any]
            Additional args to be logged, some are non-optional
        info_map["class"] : str
            The name of the class which called this function
        info_map["function"] : str
            The name of the function which called this function
        info_map["prefix"] : str, optional
            If present, overrides the automated prefix
        info_map["suppress_prefix"] : bool, optional
            If present and True, suppresses the automated prefix generation.
            Has no effect on manual prefix overrides.
        info_map["suffix"] : str, optional
            If present, gets appended to the key
        """
        info_map["timestamp"] = Utility.get_timestamp(include_millis=True)
        key = self._generate_key(name, info_map)
        self._add_to_pool(self.logs_pool, key, msg, info_map)
        self._handle_log_output(name, msg, info_map, LogVerbosity.LOGS)

    def add_warning(self, name: str, msg: str, info_map: dict[str, Any]) -> None:
        """
        Adds a warning message to the pool of warnings.

        Parameters
        ----------
        name : str
            The name of the warning
        msg : str
            The warning message to be added to the pool
        info_map: dict[str, Any]
            Additional args to be logged, some are non-optional
        info_map["class"] : str
            The name of the class which called this function
        info_map["function"] : str
            The name of the function which called this function
        info_map["prefix"] : str, optional
            If present, overrides the automated prefix
        info_map["suppress_prefix"] : bool, optional
            If present and True, suppresses the automated prefix generation.
            Has no effect on manual prefix overrides.
        info_map["suffix"] : str, optional
            If present, gets appended to the key
        """
        info_map["timestamp"] = Utility.get_timestamp(include_millis=True)
        key = self._generate_key(name, info_map)
        self._add_to_pool(self.warnings_pool, key, msg, info_map)
        self._handle_log_output(name, msg, info_map, LogVerbosity.WARNINGS)

    def add_error(self, name: str, msg: str, info_map: dict[str, Any]) -> None:
        """
        Adds an error message to the pool of errors.

        Parameters
        ----------
        name : str
            The name of the error
        msg : str
            The error message to be added to the pool
        info_map: dict[str, Any]
            Additional args to be logged, some are non-optional
        info_map["class"] : str
            The name of the class which called this function
        info_map["function"] : str
            The name of the function which called this function
        info_map["prefix"] : str, optional
            If present, overrides the automated prefix
        info_map["suppress_prefix"] : bool, optional
            If present and True, suppresses the automated prefix generation.
            Has no effect on manual prefix overrides.
        info_map["suffix"] : str, optional
            If present, gets appended to the key
        """
        info_map["timestamp"] = Utility.get_timestamp(include_millis=True)
        key = self._generate_key(name, info_map)
        self._add_to_pool(self.errors_pool, key, msg, info_map)
        self._handle_log_output(name, msg, info_map, LogVerbosity.ERRORS)

    def _handle_log_output(self, name: str, msg: str, info_map: dict[str, Any], log_level: LogVerbosity) -> None:
        """Formats log output based on log_level.

        Parameters
        ----------
        name : str
            The name of the log.
        msg : str
            The log message to be added to the pool.
        info_map : dict[str, Any]
            Additional args to be logged.
        log_level : LogVerbosity
            The LogVerbosity level.
        """
        colors: dict[LogVerbosity, str] = {
            LogVerbosity.NONE: "\033[0m",
            LogVerbosity.ERRORS: "\33[91m",
            LogVerbosity.WARNINGS: "\33[93m",
            LogVerbosity.LOGS: "\33[92m",
        }
        if log_level <= self.__log_verbose:
            log_format = "{color}[{timestamp}][{log_level}][{metadata_prefix}] {name}. {message}{color_reset}\n"
            formatted_msg = log_format.format(
                timestamp=info_map["timestamp"],
                color=colors[log_level],
                color_reset=colors[LogVerbosity.NONE],
                metadata_prefix=self.__metadata_prefix,
                name=name,
                message=msg,
                log_level=log_level,
            )
            sys.stdout.write(formatted_msg)

    def set_metadata_prefix(self, metadata_prefix: str) -> None:
        """Sets the metadata_prefix attribute."""
        self.__metadata_prefix = metadata_prefix

    def set_log_verbose(self, log_verbose: LogVerbosity = LogVerbosity.CREDITS) -> None:
        """Sets the __log_verbose attribute"""
        self.__log_verbose = log_verbose

    def _generate_key(self, name: str, info_map: dict[str, Union[str, bool]]) -> str:
        """
        Generates key for the pool.
        See "add_variable" docs for detailed arg description.

        Raises
        ------
        KeyError
            If either info_map["class"] or info_map["function"] are
            not present.
        """
        if info_map.get("class") is None:
            raise KeyError("'class' was not found in info_map")
        if info_map.get("function") is None:
            raise KeyError("'function' was not found in info_map")

        prefix = ""
        prefix_value = info_map.get("prefix")
        if isinstance(prefix_value, str):
            prefix = prefix_value + "."
        elif not info_map.get("suppress_prefix", False):
            class_value = info_map.get("class")
            function_value = info_map.get("function")
            if isinstance(class_value, str) and isinstance(function_value, str):
                prefix = self._get_prefix(class_value, function_value) + "."

        suffix = f'.{info_map.get("suffix")}' if info_map.get("suffix") is not None else ""

        return f"{prefix}{name}{suffix}"

    def _get_prefix(self, caller_class: str, caller_function: str) -> str:
        """
        Returns the prefix for a key in the pool.

        Parameters
        ----------
        caller_class : str
            Name of the class in which the call to output manager is originated
        function : str
            Name of the function which called the output manager originated

        Returns
        -------
        str
            {caller_class}.{caller_function}
        """
        return f"{caller_class}.{caller_function}"

    def _write_disclaimer(self, file_pointer: TextIO) -> None:
        """
        Writes the predefined disclaimer message to a given file.

        Parameters
        ----------
        file_pointer: TextIO
            A file-like object (supporting the `.write()` method) that points to the file where the disclaimer should
            be written.

        Example
        -------
        >>> output_manager = OutputManager()
        >>> import io
        >>> file_like_string = io.StringIO()
        >>> output_manager._write_disclaimer(file_like_string)
        >>> assert file_like_string.getvalue() == DISCLAIMER_MESSAGE + "\\n"
        """
        file_pointer.write(DISCLAIMER_MESSAGE + "\n")

    def dict_to_file_json(
        self,
        data_dict: dict[str, Any],
        path: Path,
        minify_output_file: bool = False,
        origin_label: OriginLabel = OriginLabel.NONE,
    ) -> None:
        """Saves a dictionary into a JSON file

        Parameters
        ----------
        data_dict : dict[str, Any]
            The dictionary to be saved

        path : Path
            The path to the file to be saved

        minify_output_file : bool
            Boolean flag indicating whether to minify the output JSON file.

        origin_label : OriginLabel, default OriginLabel.NONE
            The origin label specifying the format of the detailed values string.

        Raises
        ------
        Exception
            If an error occurs while saving to the file.

        Notes
        -----
        The dictionary is first converted to a serializable format using
        `Utility.make_serializable()`.

        The file is saved with no indentation.

        If you want to save time and space, limit the maximum depth of the
        serialized dictionary using the max_depth parameter. You can also set the
        `minify_output_file` flag to True to minimize the output JSON file size.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.dict_to_file_json.__name__,
        }
        self.add_log("save_dict_file_try", f"Attempting to save to {path}.", info_map)
        data_dict = {**{"DISCLAIMER": DISCLAIMER_MESSAGE}, **data_dict}
        try:
            with open(path, "w", encoding="utf-8") as json_file:
                data_dict = self._add_detailed_values(data_dict, origin_label)
                if minify_output_file:
                    json.dump(
                        Utility.make_serializable(data_dict, max_depth=self.JSON_OUTPUT_MAX_RECURSIVE_DEPTH),
                        json_file,
                        separators=(",", ":"),
                        ensure_ascii=False,
                    )
                else:
                    json.dump(
                        Utility.make_serializable(data_dict, max_depth=self.JSON_OUTPUT_MAX_RECURSIVE_DEPTH),
                        json_file,
                        indent=2,
                        ensure_ascii=False,
                    )
                self.add_log("save_dict_file_success", f"Successfully saved to {path}.", info_map)
        except Exception as e:
            raise e

    def _add_detailed_values(self, data_dict: dict[str, Any], origin_label: OriginLabel) -> dict[str, Any]:
        """
        Adds a `detailed_values` list to each sub-dictionary to replace the original `values` list.

        Parameters
        ----------
        data_dict : dict[str, Any]
            The input dictionary containing keys that may map to other dictionaries with `info_maps` and `values` keys.
            `info_maps` should contain a list of dictionaries, each with a `data_origin` key indicating the source
            of the data. `values` should contain a list of values corresponding to these origins.
        origin_label : OriginLabel
            The origin label specifying the format of the detailed values string.

        Returns
        -------
        dict[str, Any]
            The modified dictionary with a `detailed_values` list added to each sub-dictionary that meets the
            criteria. This list provides detailed information on the origins and units of each value.

        Notes
        -----
        When the OriginLabel is set to anything other than NONE, this method iterates over each key in the
        provided dictionary, and it will create a `detailed_values` list that integrates the data origins,
        values, and units. Depending on the `origin_label` parameter, the format of the detailed values will vary:

        - If `origin_label` is `OriginLabel.TRUE_AND_REPORT_ORIGINS`, the format is:
          "[true_origin_class.true_origin_function]->[report_origin]: value (units)"
          or "[true_origin_class.true_origin_function]->[report_origin]: subkey1 = value1 (units1),
           subkey2 = value2 (units2), ..." if the value is a dictionary.

        - If `origin_label` is `OriginLabel.TRUE_ORIGIN`, the format is:
          "[true_origin_class.true_origin_function]: value (units)"
          or "[true_origin_class.true_origin_function]: subkey1 = value1 (units1), subkey2 = value2 (units2), ..."
          if the value is a dictionary.

        - If `origin_label` is `OriginLabel.REPORT_ORIGIN`, the format is:
          "[report_origin]: value (units)"
          or "[report_origin]: subkey1 = value1 (units1), subkey2 = value2 (units2), ..."
          if the value is a dictionary.

        - If `origin_label` is `OriginLabel.NONE`, there will be no detailed_values information added.

        Examples
        --------
        >>> example_data_dict = {
        ...     "AnimalModuleReporter.report_daily_animal_population.num_animals": {
        ...         "info_maps": [
        ...             {"data_origin": [["AnimalManager", "daily_updates"]], "units": "animals"},
        ...             {"data_origin": [["AnimalManager", "daily_updates"]], "units": "animals"}
        ...         ],
        ...         "values": [193, 194]
        ...     },
        ...     "WeatherModuleReporter.report_daily_weather.temperature": {
        ...         "info_maps": [
        ...             {"data_origin": [["WeatherManager", "daily_temperature"]],
        ...              "units": {"avg": "°C", "min": "°C", "max": "°C"}},
        ...             {"data_origin": [["WeatherManager", "daily_temperature"]],
        ...              "units": {"avg": "°C", "min": "°C", "max": "°C"}}
        ...         ],
        ...         "values": [
        ...             {"avg": 25.5, "min": 18.2, "max": 32.1},
        ...             {"avg": 26.1, "min": 19.7, "max": 33.4}
        ...         ]
        ...     }
        ... }
        >>> output_manager = OutputManager()
        >>> modified_data_dict = output_manager._add_detailed_values(
        ...     example_data_dict, OriginLabel.TRUE_AND_REPORT_ORIGINS
        ... )
        >>> assert modified_data_dict[
        ...     "AnimalModuleReporter.report_daily_animal_population.num_animals"]["detailed_values"
        ... ] == [
        ...    "[AnimalManager.daily_updates]->[AnimalModuleReporter.report_daily_animal_population.num_animals]: "
        ...    "193 (animals)",
        ...    "[AnimalManager.daily_updates]->[AnimalModuleReporter.report_daily_animal_population.num_animals]: "
        ...    "194 (animals)"
        ... ]
        >>> assert modified_data_dict[
        ...     "WeatherModuleReporter.report_daily_weather.temperature"]["detailed_values"
        ... ] == [
        ...    "[WeatherManager.daily_temperature]->[WeatherModuleReporter.report_daily_weather.temperature]: "
        ...    "avg = 25.5 (°C), min = 18.2 (°C), max = 32.1 (°C)",
        ...    "[WeatherManager.daily_temperature]->[WeatherModuleReporter.report_daily_weather.temperature]: "
        ...    "avg = 26.1 (°C), min = 19.7 (°C), max = 33.4 (°C)"
        ... ]
        """

        if origin_label is OriginLabel.NONE:
            return data_dict

        for key, sub_data_dict in data_dict.items():
            if not self._can_add_detailed_values(sub_data_dict):
                continue

            data_origins: list[list[tuple[str, str]]] = []
            units: list[str | dict[str, str]] = []
            for info_map in sub_data_dict["info_maps"]:
                if "data_origin" not in info_map:
                    break
                if "units" not in info_map:
                    break
                data_origins.append(info_map["data_origin"])
                units.append(info_map["units"])

            if len(data_origins) != len(sub_data_dict["values"]) or len(units) != len(sub_data_dict["values"]):
                continue

            detailed_values: list[str] = []
            for index, value in enumerate(sub_data_dict["values"]):
                for origin in data_origins[index]:
                    detailed_origin_data = {
                        "true_origin_class": origin[0],
                        "true_origin_function": origin[1],
                        "report_origin": key,
                        "value": value,
                        "units": units[index],
                    }
                    detailed_value = self._format_detailed_value_str(origin_label, detailed_origin_data)
                    detailed_values.append(detailed_value)

            sub_data_dict["detailed_values"] = detailed_values

        return data_dict

    def _format_detailed_value_str(self, origin_label: OriginLabel, data: dict[str, Any]) -> str:
        """
        Formats the detailed values string based on the provided origin label and data.

        Parameters
        ----------
        origin_label : OriginLabel
            The origin label specifying the format of the detailed values string.

        data : dict[str, Any]
            A dictionary containing the necessary data for formatting the detailed values string.
            It should have the following keys:
            - "true_origin_class": The class name of the true origin.
            - "true_origin_function": The function name of the true origin.
            - "report_origin": The report origin which already includes the class and function names.
            - "value": The value associated with the origin.
            - "units": The units associated with the value.

        Returns
        -------
        str
            The formatted detailed values string based on the provided origin label and data.

        Notes
        -----
        The format of the detailed values string depends on the `origin_label` parameter:
        - If `origin_label` is `OriginLabel.TRUE_AND_REPORT_ORIGINS`, the format is:
          "[true_origin_class.true_origin_function]->[report_origin]: value (units)"
          or "[true_origin_class.true_origin_function]->[report_origin]: subkey1 = value1 (units1),
           subkey2 = value2 (units2), ..." if the value is a dictionary.

        - If `origin_label` is `OriginLabel.TRUE_ORIGIN`, the format is:
          "[true_origin_class.true_origin_function]: value (units)"
          or "[true_origin_class.true_origin_function]: subkey1 = value1 (units1), subkey2 = value2 (units2), ..."
          if the value is a dictionary.

        - If `origin_label` is `OriginLabel.REPORT_ORIGIN`, the format is:
          "[report_origin]: value (units)"
          or "[report_origin]: subkey1 = value1 (units1), subkey2 = value2 (units2), ..."
          if the value is a dictionary.

        - If `origin_label` is `OriginLabel.NONE`, there will be no detailed_values information so no formatting will
        occur.
        """

        true_origin_class = data["true_origin_class"]
        true_origin_function = data["true_origin_function"]
        report_origin = data["report_origin"]
        value = data["value"]
        units = data["units"]

        origin_label_str = ""
        if origin_label is OriginLabel.TRUE_AND_REPORT_ORIGINS:
            origin_label_str = f"[{true_origin_class}.{true_origin_function}]->[{report_origin}]"
        elif origin_label is OriginLabel.TRUE_ORIGIN:
            origin_label_str = f"[{true_origin_class}.{true_origin_function}]"
        elif origin_label is OriginLabel.REPORT_ORIGIN:
            origin_label_str = f"[{report_origin}]"

        if isinstance(value, dict) and isinstance(units, dict):
            formatted_values = [f"{subkey} = {value[subkey]} ({units[subkey]})" for subkey in value.keys()]
            return (
                f"{origin_label_str}: {', '.join(formatted_values)}"
                if origin_label_str
                else f"{', '.join(formatted_values)}"
            )

        return f"{origin_label_str}: {value} ({units})" if origin_label_str else f"{value} ({units})"

    def _can_add_detailed_values(self, sub_data_dict: dict[str, Any]) -> bool:
        """
        Checks if the provided sub_data_dict has the necessary structure and data to add detailed values.

        The sub_data_dict should meet the following requirements:
        - It must be a dictionary.
        - It must contain the keys "info_maps" and "values".
        - The length of the "info_maps" list and the "values" list must be equal.

        Notes
        -----
        The sub_data_dict should meet the following requirements:
        - It must be a dictionary.
        - It must contain the keys "info_maps" and "values".
        - The length of the "info_maps" list and the "values" list must be equal.

        Parameters
        ----------
        sub_data_dict : dict[str, Any]
            The dictionary to check for compatibility with adding detailed values.

        Returns
        -------
        bool
            True if the sub_data_dict meets the requirements for adding detailed values, False otherwise.
        """
        if not isinstance(sub_data_dict, dict):
            return False
        if "info_maps" not in sub_data_dict or "values" not in sub_data_dict:
            return False
        if not sub_data_dict["info_maps"] or not sub_data_dict["values"]:
            return False
        if len(sub_data_dict["info_maps"]) != len(sub_data_dict["values"]):
            return False
        return True

    def _dict_to_csv_column_list(self, variable_name: str, data_dict: dict[str, list[Any]]) -> list[pd.Series]:
        """Turns a dictionary to a list of csv columns.

        Parameters
        ----------
        variable_name : str
            The name of the variable having its values written into a CSV column.
        data_dict : dict[str, list[Any]]
            The dictionary to read from

        Returns
        -------
        list[pd.Series]
            A list of (column_name, column_data) tuples.

        """

        column_list = []
        units = data_dict["info_maps"][0]["units"] if data_dict.get("info_maps", []) else None
        data_list = data_dict["values"]
        if data_list and isinstance(data_list[0], dict):
            csv_column_lists: dict[str, list[Any]] = {subkey: [] for item in data_list for subkey in item.keys()}
            for nested_dictionary in data_list:
                for subkey, value in nested_dictionary.items():
                    csv_column_lists[subkey].append(value)

            for subkey in csv_column_lists.keys():
                column_title = f"{variable_name}.{subkey}{self._get_units_substr(variable_name, units, subkey)}"
                column_list.append(pd.Series(csv_column_lists[subkey], dtype=object, name=column_title))
        else:
            column_title = f"{variable_name}{self._get_units_substr(variable_name, units)}"
            column_list.append(pd.Series(data_list, dtype=object, name=column_title))

        return column_list

    def _get_units_substr(
        self, variable_name: str, units: str | dict[str, str] | None, subkey: str | None = None
    ) -> str:
        """Get the units substring for a column title.

        Parameters
        ----------
        variable_name : str
            The name of the variable or group of variables associated with the units.
        units : str | dict[str, str] | None
            The units associated with the data.
        subkey : str | None, optional
            The subkey to retrieve the units for, if units is a dictionary. Default is None.

        Returns
        -------
        str
            The formatted units substring for the column title.

        Examples
        --------
        >>> output_manager = OutputManager()
        >>> output_manager._get_units_substr("temperature", "C")
        ' (C)'
        >>> output_manager._get_units_substr("velocity", {"magnitude": "m/s", "direction": "degrees"}, "magnitude")
        ' (m/s)'
        >>> output_manager._get_units_substr("velocity", {"magnitude": "m/s", "direction": "degrees"}, "direction")
        ' (degrees)'
        >>> output_manager._get_units_substr("coordinates", {"x": "m", "y": "m"})
        ''
        """
        if not isinstance(units, dict):
            return f" ({units})" if units else ""

        if variable_name in units:
            return f" ({units[variable_name]})"

        if subkey is None:
            self.add_error(
                "units_subkey_missing",
                f"Variable {variable_name} has a dictionary for its 'units' property, "
                f"but the 'values' associated with this variable are not dictionaries themselves.",
                info_map={
                    "class": self.__class__.__name__,
                    "function": self._get_units_substr.__name__,
                },
            )
            return ""

        if subkey in units:
            return f" ({units[subkey]})"

        self.add_error(
            "units_key_error",
            f"Key '{subkey}' not found in the units dictionary for variable '{variable_name}'.",
            info_map={
                "class": self.__class__.__name__,
                "function": self._get_units_substr.__name__,
            },
        )

        return ""

    def _dict_to_file_csv(self, data_dict: dict[str, Any], path: Path, direction: str | None = "portrait") -> None:
        """
        Saves a dictionary to a csv file.

        Parameters
        ----------
        data_dict : dict[str, Any]
            The dictionary to be saved.
        path : Path
            The path to the file to be saved.
        direction : str | None
            The direction of the csv file, either portrait or landscape, default if portrait.
            If None is provided, the file will be saved in default portrait orientation.

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._dict_to_file_csv.__name__,
        }

        self.add_log("save_dict_file_try", f"Attempting to save to {path}.", info_map)

        if len(data_dict) == 0:
            self.add_log(
                "save_dict_file_try",
                f"Nothing to save to {path}. Data dictionary is empty.",
                info_map,
            )
            return

        csv_columns = []
        for variable_name, variable_data in data_dict.items():
            csv_column_data = self._dict_to_csv_column_list(variable_name, variable_data)
            csv_columns.extend(csv_column_data)

        df = pd.concat(csv_columns, axis=1)
        disclaimer_column = [DISCLAIMER_MESSAGE] + [""] * (len(df) - 1)
        disclaimer_df = pd.DataFrame({"DISCLAIMER": disclaimer_column})
        df = pd.concat([disclaimer_df, df], axis=1)

        if direction == "portrait" or direction is None:
            df.to_csv(path, index=False, encoding="utf-8")
        elif direction == "landscape":
            df.T.to_csv(path, encoding="utf-8")
        else:
            self.add_error(
                "Unknown Direction for CSV Output",
                f"The provided direction '{direction}' is not recognized. "
                f"Saving the output in portrait direction as default.",
                info_map,
            )
            df.to_csv(path, index=False, encoding="utf-8")

        self.add_log("save_dict_file_try", f"Successfully saved to {path}.", info_map)

    def _list_to_file_txt(self, data_list: list[str], path: Path) -> None:
        """Saves a list into a text file

        Parameters
        ----------
        data_list : list[str]
            The list of variable names to be saved
        path : str
            The path to the file to be saved

        Raises
        ------
        Exception
            If an error occurs while saving to the file.

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._list_to_file_txt.__name__,
        }
        self.add_log("save_txt_file_try", f"Attempting to save to {path}.", info_map)
        try:
            with open(path, "w") as var_names_file:
                self._write_disclaimer(var_names_file)
                var_names_file.writelines(data_list)
                self.add_log("save_txt_file_success", f"Successfully saved to {path}.", info_map)
        except Exception as e:
            raise e

    def generate_file_name(self, base_name: str, extension: str, include_millis: bool = False) -> str:
        """Returns a file name using the given base_name and timestamp."""

        timestamp: str = Utility.get_timestamp(include_millis=include_millis)
        return f"{self.__metadata_prefix}_{base_name}_{timestamp}.{extension}"

    def _exclude_info_maps(self, pool: dict[str, pool_element_type]) -> dict[str, pool_element_type]:
        """Makes a copy of the given pool and removes info_maps from it.

        Returns
        -------
        dict[str, OutputManager.pool_element_type]
            A copy of the given pool with info_maps removed from it.

        """
        pool_copy = pool.copy()
        for key, value in pool_copy.items():
            if isinstance(value, dict) and "info_maps" in value:
                value.pop("info_maps")
        return pool_copy

    def _list_filter_files_in_dir(self, dir_path: Path) -> list[str]:
        """Returns the list of supported filter files in the given path"""
        info_map = {
            "class": self.__class__.__name__,
            "function": self._list_filter_files_in_dir.__name__,
        }
        self.add_log(
            "search_path_for_filenames_try",
            f"Attempting to search in {dir_path}.",
            info_map,
        )
        if dir_path.is_dir():
            filter_files = []
            all_files = os.listdir(dir_path)
            for filename in all_files:
                if filename.endswith(".txt") or filename.endswith(".json"):
                    for supported_prefix in self._filter_prefixes.values():
                        if filename.startswith(supported_prefix):
                            break
                    else:
                        self.add_warning(
                            "invalid filter file prefix",
                            f"{filename} prefix is not in {list(self._filter_prefixes.values())}",
                            info_map,
                        )
                        continue
                    filter_files.append(filename)
            self.add_log(
                "search_path_for_filenames_success",
                f"Successfully searched in {dir_path}" f" and found {len(filter_files)} filter files.",
                info_map,
            )
            return filter_files
        else:
            raise NotADirectoryError("The specified path must be a directory")

    def _load_filter_file_content(self, path: Path) -> tuple[list[dict[str, Any]], str | None]:
        """
        Loads and processes the content of a filter file from the specified path.

        Parameters
        ----------
        path : Path
            The path to the filter file (either .json or .txt).

        Returns
        -------
        tuple[list[dict[str, str|int]], str]
            A tuple of:
            - A list of dictionaries, each containing the loaded filter content, with keys and values depending on the
            file type.
            - A string representing the output CSV direction, either "portrait" or "landscape". If not direction is
            specified, an empty string "" is returned.

        Raises
        ------
        FileNotFoundError
            If the specified file does not exist.

        json.JSONDecodeError
            If there is an issue with parsing a JSON file.

        UnicodeDecodeError
            If there is an issue with decoding a text file.

        Exception
            If an unsupported file format is encountered; only .json and .txt are supported.

        Notes
        -----
        This method attempts to open and process a filter file located at the specified path.
        It supports two file formats: JSON and plain text (.txt). If the file is a JSON file,
        it loads the JSON content into a dictionary. If the file is a .txt file, it reads the
        lines and creates a dictionary with a "filters" key and a list of filter elements as values.
        Unsupported file formats will raise an exception.

        This method is used to handle loading filter content from external files, which are
        used to define filtering criteria for the variables pool.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._load_filter_file_content.__name__,
        }
        self.add_log("open_filter_file", f"Attempting to open {path}.", info_map)
        try:
            with open(path) as filter_file:
                direction: str | None = None
                if path.suffix == ".json":
                    json_content = json.load(filter_file)
                    direction = json_content.get("direction", None)
                    if "multiple" in json_content.keys():
                        result = json_content["multiple"]
                    else:
                        result = [json_content]
                elif path.suffix == ".txt":
                    list_of_elements = [element for element in filter_file.read().splitlines() if element]
                    filter_by_exclusion = list_of_elements[0] == "exclude"
                    if filter_by_exclusion:
                        list_of_elements.pop(0)
                    result = [{"filters": list_of_elements, "filter_by_exclusion": filter_by_exclusion}]
                else:
                    raise Exception("Unsupported file format; only json and txt are supported.")
            self.add_log("text_file_load_log", f"Successfully opened {path}.", info_map)
            return result, direction
        except FileNotFoundError:
            self.add_error("File not found", f"The file '{path}' does not exist.", info_map)
            raise
        except json.JSONDecodeError as e:
            self.add_error("JSON parsing error", str(e), info_map)
            raise
        except UnicodeDecodeError as e:
            self.add_error("Text decoding error", str(e), info_map)
            raise
        except Exception as e:
            self.add_error("Unexpected error", str(e), info_map)
            raise

    def filter_variables_pool(
        self,
        filter_content: dict[str, Any],
    ) -> dict[str, pool_element_type]:
        """
        Returns a filtered variables pool based on options specified in filter_content.

        Parameters
        ----------
        filter_content : dict[str, Any]
            A dictionary that contains filtering options.

        Returns
        -------
        dict[str, OutputManager.pool_element_type]
            A filtered variables pool based on either inclusion or exclusion.
        """
        filter_name: str = filter_content.get("name", "NO NAME FOUND")
        use_filter_name: bool = filter_content.get("use_name", False)
        filter_by_exclusion: bool = filter_content.get("filter_by_exclusion", False)
        use_filter_key_name: bool = filter_content.get("use_filter_key_name", False)
        info_map = {
            "class": self.__class__.__name__,
            "function": self.filter_variables_pool.__name__,
            "filter_name": filter_name,
            "filter_by_exclusion": filter_by_exclusion,
            "use_filter_name": use_filter_name,
        }
        if filter_by_exclusion:
            filter_excl_msg = f"Performing filtering by exclusion per filter's contents. {filter_name=}"
        else:
            filter_excl_msg = f"Performing filtering by inclusion per filter's contents. {filter_name=}"
        self.add_log("filtering_log", filter_excl_msg, info_map)

        filtered_pool: dict[str, OutputManager.pool_element_type] = Utility.filter_dictionary(
            dict_to_filter=self._get_flat_variables_pool(),
            filter_patterns=filter_content.get("filters", []),
            filter_by_exclusion=filter_by_exclusion,
        )
        self.add_log(
            "num_filter_pattern_matches",
            f"There were {len(filtered_pool)} matches for filter pattern(s) in {filter_name=}.",
            info_map,
        )

        selected_variables: list[str] | None = filter_content.get("variables")

        results = self._parse_filtered_variables(
            filtered_pool, selected_variables, filter_name, use_filter_name, filter_by_exclusion, use_filter_key_name
        )

        if filter_content.get("expand_data", False):
            fill_value = filter_content.get("fill_value", np.nan)
            use_fill_value_in_gaps = filter_content.get("use_fill_value_in_gaps", True)
            use_fill_value_at_end = filter_content.get("use_fill_value_at_end", True)
            try:
                results = Utility.expand_data_temporally(
                    results,
                    fill_value=fill_value,
                    use_fill_value_in_gaps=use_fill_value_in_gaps,
                    use_fill_value_at_end=use_fill_value_at_end,
                )
            except (TypeError, ValueError) as e:
                error_title = f"Error {e} raised when padding data"
                error_msg = f"Unable to pad data for variables gathered for {filter_name=}."
                self.add_error(error_title, error_msg, info_map)

        slice_start: int = filter_content.get("slice_start", 0)
        slice_end: int | None = filter_content.get("slice_end", None)
        for key in results.keys():
            if "info_maps" in results[key].keys():
                results[key]["info_maps"] = results[key]["info_maps"][slice_start:slice_end]
            results[key]["values"] = results[key]["values"][slice_start:slice_end]

        return results

    def _parse_filtered_variables(
        self,
        filtered_pool: dict[str, OutputManager.pool_element_type],
        selected_variables: list[str] | None,
        filter_name: str,
        use_filter_name: bool,
        filter_by_exclusion: bool,
        use_filter_key_name: bool,
    ) -> dict[str, OutputManager.pool_element_type]:
        """
        Unpacks and counts variables that have been filtered out of the Output Manager's variables pool.

        Parameters
        ----------
        filtered_pool : dict[str, OutputManager.pool_element_type]
            Variables that have been filtered out of the Output Manager's pool.
        selected_variables : list[str] | None
            list of key names to select or exclude from variables containing dictionaries.
        filter_name : str
            Name of the filter used to collect variables for the filtered pool.
        use_filter_name : bool
            Whether to use the filter name when constructing the key name for data pulled from the filtered pool.
        filter_by_exclusion : bool
            Whether keys in dictionaries should be filtered by exclusion.
        use_filter_key_name : bool
            Whether to use the filtered key name when constructing the key name for data pulled from a dictionary.

        Returns
        -------
        dict[str, OutputManager.pool_element_type]
            Dictionary containing data from the filtered pool of data, with data from within dictionaries unpacked and
            separated.

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._parse_filtered_variables.__name__,
            "filter_name": filter_name,
            "filter_by_exclusion": filter_by_exclusion,
            "use_filter_name": use_filter_name,
        }
        results: dict[str, OutputManager.pool_element_type] = {}
        counter: int = 0
        for key in filtered_pool.keys():
            info_maps: list[dict[str, Any]] = (
                filtered_pool[key]["info_maps"] if "info_maps" in filtered_pool[key] else []
            )
            data: list[Any] = filtered_pool[key]["values"]
            is_data_in_dict: bool = all(isinstance(element, dict) for element in data)
            if selected_variables is None or not is_data_in_dict:
                combined_key = f"{filter_name}_{counter}" if use_filter_name else key
                results[combined_key] = ({"info_maps": info_maps} if info_maps else {}) | {"values": data}
                self._variables_usage_counter.update([key])
            elif is_data_in_dict:
                if not isinstance(selected_variables, list):
                    self.add_error(
                        "Unpacking Pool Error",
                        f"Unable to unpack {key=} in the data pool, need a valid `variables` entry for this entry."
                        f"{is_data_in_dict=}, {selected_variables=}, see Wiki for proper setup details.",
                        info_map,
                    )
                temp_data = Utility.convert_list_of_dicts_to_dict_of_lists(data)
                filtered_data = Utility.filter_dictionary(temp_data, selected_variables, filter_by_exclusion)
                for filtered_key, filtered_value in filtered_data.items():
                    if use_filter_key_name:
                        # TODO DEPRECATED behavior, kept for backward compatibility
                        # should be removed when closing #2718
                        combined_key = filtered_key
                    else:
                        combined_key = (
                            f"{filter_name}_{counter}.{filtered_key}" if use_filter_name else f"{key}.{filtered_key}"
                        )
                    if combined_key in results.keys():
                        results[combined_key].get("info_maps", []).extend(info_maps)
                        results[combined_key]["values"].extend(filtered_value)
                    else:
                        results[combined_key] = ({"info_maps": info_maps} if info_maps else {}) | {
                            "values": filtered_value
                        }
                    self._variables_usage_counter.update([f"{key}.{filtered_key}"])
            counter += 1
        return results

    def _sort_saved_chunk_files(self) -> list[Path]:
        """
        Get a list of all saved chunks of the output variable pool by retrieving all JSON files under
        the saved_pool_chunks_path. Then sort the files according to their file name to preserve the order.
        """
        list_of_dumped_files: list[Path] = [
            file for file in self.saved_pool_chunks_path.iterdir() if file.is_file() and file.name.endswith(".json")
        ]
        list_of_dumped_files.sort(key=lambda file_name: int((str(file_name).split("saved_pool_")[1]).split("_")[0]))
        return list_of_dumped_files

    def load_saved_pools(self) -> None:
        """
        Loads saved pools of data from JSON files in the saved_pool_chunks_path directory and merges them into
        a single variables pool.
        """
        merged_pool: dict[str, OutputManager.pool_element_type] = {}
        list_of_dumped_files = self._sort_saved_chunk_files()
        for file in list_of_dumped_files:
            self.load_variables_pool_from_file(file)
            for key, value in self.variables_pool.items():
                if key not in merged_pool:
                    merged_pool[key] = value
                else:
                    merged_pool[key]["info_maps"].extend(value["info_maps"])
                    merged_pool[key]["values"].extend(value["values"])
            self.current_pool_size = 0
            self._set_variables_pool({}, pool_size_override=0)

        self._set_variables_pool(merged_pool, pool_size_override=sys.getsizeof(merged_pool))

    def save_results(  # noqa: C901
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

        Notes
        -----
        The filter files can be used to generate different output formats such as JSON, CSV, and graphical output.

        Parameters
        ----------
        filters_dir_path : Path
            Path of the directory containing the files containing the keys for filtering.
        exclude_info_maps : bool
            Flag for whether or not the user wants to include info_maps data in their results files.
        produce_graphics: bool
            Flag for whether or not the user wants to produce graphs at after the simulation.
        report_dir : Path
            The directory for saving reports to.
        graphics_dir : Path
            The directory for saving graphics.
        csv_dir : Path
            The directory for saving csvs.
        json_dir : Path
            The directory for saving JSONs containing filtered simulation output.

        """
        info_map: dict[str, Any] = {
            "class": self.__class__.__name__,
            "function": self.save_results.__name__,
        }
        self.add_log(
            "exclude_info_maps",
            f"exclude_info_maps flag set to {exclude_info_maps}",
            info_map,
        )
        has_cross_references = False
        has_data_significant_digits = False
        cross_ref_reports: list[str] = []
        limited_significant_digits_reports: list[str] = []
        list_of_filter_files = self._list_filter_files_in_dir(filters_dir_path)
        report_generator = ReportGenerator(self.time)
        if self.chunkification:
            self._save_current_variable_pool()
            self.load_saved_pools()
        for filter_file in list_of_filter_files:
            info_map["filter file"] = filter_file
            input_path = filters_dir_path / filter_file
            filter_contents, direction = self._load_filter_file_content(input_path)
            if filter_file.startswith(self.__supported_filter_types_prefixes["report"]):
                self.add_log(
                    "init_report_generation",
                    f"Generating report for file: {filter_file}",
                    info_map,
                )
            for filter_content in filter_contents:
                info_map["filter_content"] = filter_content
                if not isinstance(filter_content, dict) or (
                    "filters" not in filter_content.keys() and "cross_references" not in filter_content.keys()
                ):
                    self.add_error(
                        "Parsing error",
                        f"Could not parse {filter_content.get('name')=} in {filter_file=},\
                            it has to have JSON blobs and have `filters` entry."
                        f"The `filters` can only be skipped if `references` entry is present "
                        f"and the purpose is to generate a derived report.",
                        info_map,
                    )
                    continue

                filtered_pool: dict[str, OutputManager.pool_element_type] = {}
                if "filters" in filter_content.keys():
                    filtered_pool = self.filter_variables_pool(filter_content)
                if exclude_info_maps:
                    filtered_pool = self._exclude_info_maps(filtered_pool)

                if filter_file.startswith(self.__supported_filter_types_prefixes["report"]):
                    if "cross_references" in filter_content:
                        has_cross_references = True
                        cross_ref_reports.append(str(filter_content.get("name", input_path.stem)))
                    if "data_significant_digits" in filter_content:
                        has_data_significant_digits = True
                        limited_significant_digits_reports.append(str(filter_content.get("name", input_path.stem)))
                    if filter_content.get("graph_details"):
                        filter_content["graph_details"]["graphics_dir"] = graphics_dir
                        filter_content["graph_details"]["produce_graphics"] = produce_graphics
                        filter_content["graph_details"]["metadata_prefix"] = self.__metadata_prefix
                        self.create_directory(graphics_dir)
                    log_pool = report_generator.generate_report(filter_content, filtered_pool)
                    self.route_logs(log_pool)
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
            report_file_path = report_dir / self.generate_file_name(f"report_{filter_file}", "csv")
            if report_generator.reports:
                if has_cross_references and has_data_significant_digits:
                    significant_digits_limited_reports = ", ".join(
                        f"'{report}'" for report in limited_significant_digits_reports
                    )
                    cross_referenced_reports = ", ".join(f"'{report}'" for report in cross_ref_reports)
                    self.add_warning(
                        "Report Generation Warning",
                        "Reports generated have both cross references and data significant digits. "
                        "Significant digits were limited for the following reports: "
                        f"{significant_digits_limited_reports}. "
                        "Results may be affected for the following cross-referenced reports: "
                        f"{cross_referenced_reports}.",
                        info_map,
                    )
                self.create_directory(report_dir)
                self._dict_to_file_csv(report_generator.reports, report_file_path, direction)
                report_generator.clear_reports()

    def _route_save_functions(
        self,
        filter_file: str,
        filtered_pool: dict[str, pool_element_type],
        produce_graphics: bool,
        filter_content: dict[str, str | int],
        json_dir: Path,
        graphics_dir: Path,
        csv_dir: Path,
        direction: str | None,
    ) -> None:
        """
        Checks the prefix of the filter_file to determine the format for saving. It then delegates the
        saving process to the corresponding function to handle specific formats such as JSON, CSV, or graphical output.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._route_save_functions.__name__,
        }
        if "data_significant_digits" in filter_content:
            filtered_pool = {
                key: (
                    Utility.round_numeric_values_in_dict(value, int(filter_content["data_significant_digits"]))
                    if isinstance(value, dict)
                    else value
                )
                for key, value in filtered_pool.items()
            }
            self.add_log(
                "Rounding Values",
                f"Rounded values to {filter_content['data_significant_digits']} significant digits",
                info_map,
            )
        is_json = filter_file.startswith(self._filter_prefixes.get("json", "Better than a key error."))
        if is_json and self.is_first_post_processing:
            self.create_directory(json_dir)
            self._save_to_json(
                filter_file,
                json_dir,
                filtered_pool,
                filter_content,
            )
            return
        if filter_file.startswith(self._filter_prefixes.get("csv", "Better than a key error.")):
            self.create_directory(csv_dir)
            variable_csv_file_path = csv_dir / self.generate_file_name(f"saved_variables_{filter_file}", "csv")
            self._dict_to_file_csv(filtered_pool, variable_csv_file_path, direction)
            return
        if filter_file.startswith(self._filter_prefixes.get("graph", "Better than a key error.")):
            self.create_directory(graphics_dir)
            if produce_graphics:
                try:
                    graph_generator = GraphGenerator(self.__metadata_prefix, self.time)
                    log_pool = graph_generator.generate_graph(
                        filtered_pool, filter_content, filter_file, graphics_dir, produce_graphics
                    )
                    self.route_logs(log_pool)
                except Exception as e:
                    self.add_error("graph generation exception", str(e), info_map)
            else:
                self.add_warning(
                    "No Graphics",
                    f"Graphic generation is disabled, skipping {filter_file=}",
                    info_map,
                )
            return
        is_comparison = filter_file.startswith(self._filter_prefixes.get("comparison", "Better than a key error."))
        if is_comparison and not self.is_first_post_processing:
            self.create_directory(json_dir)
            self._save_to_json(
                filter_file,
                json_dir,
                filtered_pool,
                filter_content,
            )

    def _save_to_json(
        self,
        filter_file: str,
        save_path: Path,
        filtered_pool: dict[str, pool_element_type],
        filter_content: dict[str, Union[str, int]],
    ) -> None:
        """
        Saves the filtered pool to a JSON file.

        Parameters
        ----------
        filter_file : str
            The name of the filter file being processed.
        save_path : Path
            The directory path where the JSON file will be saved.
        filtered_pool : dict[str, pool_element_type]
            The pool of filtered data to be saved.
        filter_content : dict[str, Union[str, int]]
            Additional content from the filter that might influence the file naming.
        """
        if "e2e_comparison" in filter_file:
            base_name = f"comparison_{filter_content['name']}"
        elif "name" in filter_content:
            base_name = f"saved_variables_{filter_content['name']}"
        else:
            base_name = f"saved_variables_{filter_file}"

        origin_label = self._get_origin_label(filter_content)
        file_name = self.generate_file_name(base_name, "json")
        file_path = save_path / file_name
        self.dict_to_file_json(filtered_pool, file_path, origin_label=origin_label)

    def route_logs(self, log_pool: list[dict[str, str | dict[str, str]]]) -> None:
        """Takes logs from other classes and routes them to the appropriate pools in
        Output Manager.

        Parameters
        ----------
        log_pool : list[dict[str, str | dict[str, str]]]
            A list of log, warning, and error dictionaries containing all the components needed
            to log the information to the appropriate pool.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.route_logs.__name__,
        }
        for log in log_pool:
            try:
                if "error" in log:
                    if (
                        isinstance(log["error"], str)
                        and isinstance(log["message"], str)
                        and isinstance(log["info_map"], dict)
                        and list(log.keys()) == ["error", "message", "info_map"]
                    ):
                        self.add_error(log["error"], log["message"], log["info_map"])
                    else:
                        self.add_warning(
                            "Wrong format for adding error.",
                            f"Unable to add error with the format: {log}",
                            info_map,
                        )
                elif "log" in log:
                    if (
                        isinstance(log["log"], str)
                        and isinstance(log["message"], str)
                        and isinstance(log["info_map"], dict)
                        and list(log.keys()) == ["log", "message", "info_map"]
                    ):
                        self.add_log(log["log"], log["message"], log["info_map"])
                    else:
                        self.add_warning(
                            "Wrong format for adding log.",
                            f"Unable to add log with the format: {log}",
                            info_map,
                        )
                elif "warning" in log:
                    if (
                        isinstance(log["warning"], str)
                        and isinstance(log["message"], str)
                        and isinstance(log["info_map"], dict)
                        and list(log.keys()) == ["warning", "message", "info_map"]
                    ):
                        self.add_warning(log["warning"], log["message"], log["info_map"])
                    else:
                        self.add_warning(
                            "Wrong format for adding warning.",
                            f"Unable to add warning with the format: {log}",
                            info_map,
                        )
                else:
                    self.add_warning(
                        "Unsupported event key for output manager",
                        f"Output manager can add logs, errors and warnings."
                        f"Valid first key: error, log ,warning"
                        f"Valid second key: message"
                        f"Valid third key: info_map"
                        f"Given event contains the key {log.keys()}",
                        info_map,
                    )
            except KeyError:
                self.add_error(
                    "Wrong key for message or info map when reporting collected errors, logs," " warnings",
                    f'The key should be "message" for message, and "info_map" for info map.' f" Got keys: {log.keys()}",
                    info_map,
                )

    def dump_logs(self, path: Path) -> None:
        """
        Dumps logs_pool into a json file in the given path to a directory.
        """
        file_path = path / self.generate_file_name("logs", "json")
        self.dict_to_file_json(self.logs_pool, file_path)

    def dump_warnings(self, path: Path) -> None:
        """
        Dumps warnings_pool into a json file in the given path to a directory.
        """
        file_path = path / self.generate_file_name("warnings", "json")
        self.dict_to_file_json(self.warnings_pool, file_path)

    def dump_errors(self, path: Path) -> None:
        """
        Dumps errors_pool into a json file in the given path to a directory.
        """
        file_path = path / self.generate_file_name("errors", "json")
        self.dict_to_file_json(self.errors_pool, file_path)

    def report_variables_usage_counts(self, path: Path) -> None:
        """
        Reports the usage counts of variables in the variables pool to a CSV file in the given path to a directory.

        Parameters
        ----------
        path : Path
            The path to the directory where the file will be saved.
        """

        filename = self.generate_file_name("variables_usage_counts", "csv")
        file_path_csv = path / filename
        sorted_variables_usage_counter_desc = self._variables_usage_counter.most_common()
        variable_name_col = {"values": [variable[0] for variable in sorted_variables_usage_counter_desc]}
        usage_count_col = {"values": [variable[1] for variable in sorted_variables_usage_counter_desc]}
        data_dict = {"variable_name": variable_name_col, "usage_count": usage_count_col}
        self._dict_to_file_csv(data_dict, file_path_csv)

    def dump_variable_names_and_contexts(  # noqa: C901
        self,
        path: Path,
        exclude_info_maps: bool,
        format_option: str,
    ) -> None:
        """
        Dumps names of all variables added to variables_pool along with the caller class
        and function contextual information into a txt file in the given path to a directory.

        Parameters
        ----------
        path : str
            The path to the file to be dumped to.

        exclude_info_maps : bool
            Flag to denote whether info_map data should be dumped with variable names.

        format_option : {"block", "inline", "verbose", "basic"}
            The selection for the formatting option of the text written to the variables names text file.

        Examples
        --------
        For the different format options available:

        format_option: str = "basic" - Excludes information about whether data is from info_maps but has the same
                                       format as output CSV column headers.
        class_name.function_name.variable_name1.sub_variable1_name
        class_name.function_name.variable_name1.sub_variable2_name
        class_name.function_name.variable_name2.sub_variable1_name
        class_name.function_name.variable_name3

        format_option: str = "block"
        class_name.function_name.variable_name
                                            .values: variable1_name
                                            .values: variable2_name
                                            .info_maps: variable3_name
                                            .info_maps: variable4_name

        format_option: str = "inline"
        class_name.function_name.variable_name.values: [variable1_name, variable2_name]
        class_name.function_name.variable_name.info_maps: [variable3_name, variable4_name]

        format_option: str = "verbose"
        class_name.function_name.variable_name.values: variable1_name
        class_name.function_name.variable_name.values: variable2_name
        class_name.function_name.variable_name.info_maps: variable3_name
        class_name.function_name.variable_name.info_maps: variable4_name
        """

        var_list = [f"_{exclude_info_maps=}, expect info_maps accordingly.{os.linesep}"]
        for name, variable_data in self._get_flat_variables_pool().items():
            if "values" not in variable_data:
                var_list.append(f"{name}: **NO VARIABLES**{os.linesep}")
                continue

            parsable_dicts = []

            var_data_info_maps: list[Any] | None = []
            if not exclude_info_maps and "info_maps" in variable_data:
                parsable_dicts.append("info_maps")
                var_data_info_maps = variable_data.get("info_maps")

            units = var_data_info_maps[0]["units"] if var_data_info_maps else ""
            is_variable_nested = isinstance(variable_data["values"][0], dict)
            if is_variable_nested:
                parsable_dicts.append("values")
            else:
                var_list.append(f"{name} ({units}){os.linesep}" if units else f"{name}{os.linesep}")

            prefix = name
            if format_option == "block":
                if f"{name}{os.linesep}" not in var_list:
                    var_list.append(f"{name}{os.linesep}")
                prefix = " " * len(name)
            keys_to_ignore = [
                "units",
                "timestep",
                "info_maps",
                "prefix",
                "suffix",
                "data_origin",
                "number_animals_in_pen",
                "simulation_day",
            ]
            for parsable_dict in parsable_dicts:
                keys = variable_data[parsable_dict][0].keys()
                if format_option == "inline":
                    var_list.append(
                        f"{name}.{parsable_dict}: {list(keys)} ({units}){os.linesep}"
                        if not parsable_dict.endswith("info_maps") and units
                        else f"{name}.{parsable_dict}: {list(keys)}{os.linesep}"
                    )
                else:
                    for key in keys:
                        if isinstance(units, dict):
                            var_units = units.get(key, "")
                        else:
                            var_units = units
                        if format_option == "basic":
                            var_list.append(
                                f"{name}.{key} ({var_units}){os.linesep}"
                                if key not in keys_to_ignore and var_units
                                else f"{name}.{key}{os.linesep}"
                            )
                        else:
                            var_list.append(
                                f"{prefix}.{parsable_dict}: {key} ({var_units}){os.linesep}"
                                if key not in keys_to_ignore and var_units
                                else f"{prefix}.{parsable_dict}: {key}{os.linesep}"
                            )

        file_path = path / self.generate_file_name("variable_names", "txt")
        self._list_to_file_txt(var_list, file_path)

    def dump_all_nondata_pools(
        self,
        path: Path,
        exclude_info_maps: bool,
        format_option: str,
    ) -> None:
        """
        Dumps all non-data pools into the given path to a directory.
        """
        self.create_directory(path)
        self.dump_variable_names_and_contexts(path, exclude_info_maps, format_option)
        self.dump_logs(path)
        self.dump_warnings(path)
        self.dump_errors(path)
        self.report_variables_usage_counts(path)

    def _set_variables_pool(
        self,
        new_pool: dict[str, OutputManager.pool_element_type],
        *,
        pool_size_override: int | None = None,
    ) -> None:
        """Assigns the variables pool and updates the cached size.

        Parameters
        ----------
        new_pool : dict[str, OutputManager.pool_element_type]
            The new variables pool to be assigned.
        pool_size_override : int | None, optional
            If provided, this value will be used to set the current pool size instead of calculating it.
        """

        self.variables_pool = new_pool
        if pool_size_override is not None:
            self.current_pool_size = pool_size_override
            return

        self.current_pool_size = sys.getsizeof(new_pool.__repr__())

    def _get_flat_variables_pool(self) -> dict[str, Any]:
        """Returns a flattened mapping of variable names to data when multiple pools are loaded."""

        if not self.variables_pool:
            return {}

        if all(
            isinstance(variable_data, dict) and "values" in variable_data
            for variable_data in self.variables_pool.values()
        ):
            return self.variables_pool

        flattened: dict[str, Any] = {}
        for pool_name, pool_data in self.variables_pool.items():
            if not isinstance(pool_data, dict):
                continue
            for variable_name, variable_data in pool_data.items():
                flattened[f"{pool_name}.{variable_name}"] = variable_data

        return flattened

    def flush_pools(self) -> None:
        """
        Sets each pool to an empty dictionary.
        """
        self._set_variables_pool({})
        self.warnings_pool = {}
        self.errors_pool = {}
        self.logs_pool = {}

    def _read_variables_pool_file(
        self,
        file_path: Path,
        info_map: dict[str, Any],
    ) -> dict[str, list[Any]]:
        """Reads a variables pool JSON file and returns its contents."""

        self.add_log("open_json_file", f"Attempting to open {str(file_path)}.", info_map)
        try:
            with open(file_path) as file:
                loaded_pool: dict[str, list[Any]] = json.load(file)
                loaded_pool.pop("DISCLAIMER", None)
                self.add_log(
                    "load_data_successful",
                    f"Successfully loaded data from {str(file_path)}.",
                    info_map,
                )
                return loaded_pool
        except FileNotFoundError:
            self.add_error(
                "File not found",
                f"The file '{str(file_path)}' does not exist.",
                info_map,
            )
            raise
        except json.JSONDecodeError as e:
            self.add_error("JSON parsing error", str(e), info_map)
            raise

    def load_variables_pool_from_file(self, file_path: Path) -> None:
        """Loads the Output Manager variables pool from file path provided by user.

        Parameters
        ----------
        file_path : Path
            The path to the file to be loaded to the variables pool.

        Raises
        ------
        FileNotFoundError
            If the variables pool file does not exist at the specified path.
        json.JSONDecodeError
            If there is an error in decoding the JSON file.

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.load_variables_pool_from_file.__name__,
        }
        loaded_pool = self._read_variables_pool_file(file_path, info_map)
        self._set_variables_pool(loaded_pool)

    def load_multiple_variables_pools_from_files(self, pools: Sequence[tuple[str, Path] | dict[str, Any]]) -> None:
        """Loads multiple Output Manager variable pools, namespacing each pool's entries.

        Parameters
        ----------
        pools : Sequence[tuple[str, Path] | dict[str, Any]]
            An iterable of pool descriptors. Each descriptor must provide a pool name and the
            path to the JSON file containing the pool to load. When dicts are provided they
            must include ``"name"`` and ``"path"`` keys.

        """

        info_map_base = {
            "class": self.__class__.__name__,
            "function": self.load_multiple_variables_pools_from_files.__name__,
        }

        separated_pools: dict[str, OutputManager.pool_element_type] = {}
        normalized_pools: list[tuple[str, Path]] = []
        for pool in pools:
            if isinstance(pool, tuple):
                pool_name, pool_path = pool
            else:
                pool_name = pool["name"]
                pool_path = pool["path"]
            if not isinstance(pool_path, Path):
                pool_path = Path(pool_path)
            normalized_pools.append((pool_name, pool_path))

        for pool_name, pool_path in normalized_pools:
            pool_info_map = {**info_map_base, "pool_name": pool_name}
            loaded_pool = self._read_variables_pool_file(pool_path, pool_info_map)
            separated_pools[pool_name] = loaded_pool

        self._set_variables_pool(separated_pools)

    def clear_output_dir(self, vars_file_path: Path, output_dir: Path) -> None:
        """Clears the output directory if vars_file_path not in output directory.

        Parameters
        ----------
        vars_file_path : Path
            Path to file used to load Output Manager vars pool.
        output_dir : Path
            The directory for saving output.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.clear_output_dir.__name__,
        }
        is_file_found_in_dir = self.is_file_in_dir(output_dir, vars_file_path)
        if is_file_found_in_dir:
            self.add_error(
                "Can't clear output directory",
                f"{vars_file_path} in output directory.",
                info_map,
            )
        else:
            keep_list = [".keep", "output_filters"]
            Utility.empty_dir(output_dir, keep=keep_list)
            self.add_log(
                "Output directory successfully cleared",
                "Provided variables-file path was not in output directory.",
                info_map,
            )

    def is_file_in_dir(self, dir_path: Path, file_path: Path) -> bool:
        """Checks if a file path is in the provided directory.

        Parameters
        ----------
        dir_path : Path
            Path to the directory to be checked.
        file_path : Path
            Path to file to be checked.
        """
        if file_path is None:
            return False
        file_path = file_path.resolve()
        directory_path = dir_path.resolve()

        return directory_path == file_path or directory_path in file_path.parents

    def create_directory(self, path: Path) -> None:
        """
        Creates a dir from the provided path if it does not already exist.

        Parameters
        ----------
        path : Path
            The path where the directory will be created if it does not already exist.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.create_directory.__name__,
        }
        self.add_log(
            "Attempting to create a new directory.",
            f"Attempting to create a new directory at {path}.",
            info_map,
        )
        try:
            path.mkdir(parents=True, exist_ok=True)
            self.add_log(
                "Directory successfully created.",
                f"Created a new directory at {path}.",
                info_map,
            )
        except PermissionError as e:
            self.add_error("Permission Error", f"{path=}; Exception: {str(e)}", info_map)
        except Exception as e:
            self.add_error("mkdir failure", f"{path=}; Exception: {str(e)}", info_map)

    def _get_errors_warnings_logs_counts(self) -> tuple[int, int, int]:
        """
        Get the total number of errors, warnings, and logs in the output manager's errors, warnings, and logs pools.

        Returns
        -------
        tuple[int, int, int]
            The total number of errors, warnings, and logs in the output manager's errors, warnings, and logs pools.
        """

        errors_count = sum([len(value_dict["values"]) for value_dict in self.errors_pool.values()])
        warnings_count = sum([len(value_dict["values"]) for value_dict in self.warnings_pool.values()])
        logs_count = sum([len(value_dict["values"]) for value_dict in self.logs_pool.values()])
        return errors_count, warnings_count, logs_count

    def print_credits(self, version_number: str) -> None:
        """
        Prints out the RuFaS credits when LogVerbosity is set to any level except None.
        """
        if self.__log_verbose >= LogVerbosity.CREDITS:
            sys.stdout.write(f"RuFaS: Ruminant Farm Systems Model. Version: {version_number}\n{DISCLAIMER_MESSAGE}\n")

    def print_task_id(self, task_id: str) -> None:
        """
        Prints out the RuFaS credits when LogVerbosity is set to any level except None.
        """
        if self.__log_verbose >= LogVerbosity.CREDITS:
            sys.stdout.write(f"Starting task: {task_id}\n")

    def print_errors_warnings_logs_counts(self, task_id: str) -> None:
        """
        Prints out the RuFaS credits when LogVerbosity is set to any level except None.
        """
        if self.__log_verbose >= LogVerbosity.CREDITS:
            errors_count, warnings_count, logs_count = self._get_errors_warnings_logs_counts()
            sys.stdout.write(
                f"Finished task: {task_id} with {errors_count} error(s), "
                f"{warnings_count} warning(s), and {logs_count} log(s).\n"
            )

    def summarize_e2e_test_results(self, json_output_directory: Path, output_prefixes: list[str]) -> None:
        """
        Summarizes the end-to-end test results by gathering the results from all the e2e tests and readies them to be
        printed out to the console.
        This method is intended to be called at the end of an end-to-end testing run.

        Parameters
        ----------
        json_output_directory : Path
            The directory where the JSON output files are located.
        output_prefixes : list[str]
            A list of output prefixes to look for in the filenames.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.summarize_e2e_test_results.__name__,
        }
        self.add_log(
            "Attempting to open e2e test results directory",
            "Opening e2e test results directory to read results files",
            info_map,
        )
        module_headers: list[str] = ["Animal", "CropAndSoil", "Manure"]
        e2e_results_summary: dict[str, dict[str, bool | str]] = {
            prefix: {header: "n/a" for header in module_headers} for prefix in output_prefixes
        }
        all_results_files = os.listdir(json_output_directory)
        for filename in all_results_files:
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

            for key, value in data.items():
                if key == "DISCLAIMER":
                    continue
                module = self._normalize_module_header(key)
                e2e_results_summary[matched_prefix][module] = value["values"][0]

        self.add_log(
            "Successfully opened e2e test results directory", "Directory opened and files successfully read", info_map
        )

        self._print_e2e_results_summary(e2e_results_summary)

    def _print_e2e_results_summary(self, e2e_results_summary: dict[str, dict[str, bool | str]]) -> None:
        """
        Prints the end-to-end results summary to the console.
        """
        sys.stdout.write("Summary of e2e results:\n\n")
        for prefix, results in e2e_results_summary.items():
            sys.stdout.write(f"{prefix} results:\n")
            for module, result in results.items():
                result = "Passing" if result is True else "Failing" if result is False else result
                sys.stdout.write(f"  {module}: {result}\n")
            sys.stdout.write("\n")

    @staticmethod
    def _normalize_module_header(json_key: str) -> str:
        """
        Normalizes the module header from a JSON key.
        """
        module = json_key.split(".", 1)[0].lower()
        if module == "animal":
            return "Animal"
        if module == "crop_and_soil":
            return "CropAndSoil"
        if module == "manure":
            return "Manure"
        return json_key.split(".", 1)[0]

    def set_exclude_info_maps_flag(self, exclude_info_maps: bool) -> None:
        """
        Sets the exclude_info_maps flag to the given value.
        Parameters
        ----------
        exclude_info_maps : bool
            The value to set the exclude_info_maps flag to.
        """

        self._exclude_info_maps_flag = exclude_info_maps

    def _get_origin_label(self, filter_content: dict[str, str | int]) -> OriginLabel:
        """
        Retrieves the origin label from the provided filter content.

        Parameters
        ----------
        filter_content : dict[str, str | int]
            A dictionary containing filter information, which may include the "origin_label" key.

        Returns
        -------
        OriginLabel
            The origin label corresponding to the value in the filter content.
            If the "origin_label" key is not present or has an invalid value, OriginLabel.NONE is returned.

        Notes
        -----
        This method checks the value of the `origin_label` key in the provided `filter_content` dictionary.
        If the value is a valid string matching one of the supported options defined in the `OriginLabel` enum,
        the corresponding `OriginLabel` member is returned. If the value is invalid or the key is not present,
        `OriginLabel.NONE` is returned, and an error is added to the Output Manager's errors pool.
        """

        if "origin_label" not in filter_content:
            return OriginLabel.NONE

        origin_label_value = filter_content["origin_label"]
        supported_options = [label.value for label in OriginLabel]

        if not isinstance(origin_label_value, str):
            self.add_error(
                "invalid_origin_label",
                f"Origin label must be a string. Received '{origin_label_value}' of type {type(origin_label_value)}.",
                info_map={
                    "class": self.__class__.__name__,
                    "function": self._get_origin_label.__name__,
                },
            )
            return OriginLabel.NONE

        if origin_label_value not in supported_options:
            self.add_error(
                "invalid_origin_label",
                f"Origin label must be one of {supported_options}. Received '{origin_label_value}'.",
                info_map={
                    "class": self.__class__.__name__,
                    "function": self._get_origin_label.__name__,
                },
            )
            return OriginLabel.NONE

        return OriginLabel(origin_label_value)

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
        """Performs various tasks that are needed to setup and run the Output Manager."""
        self.print_task_id(task_id)
        self.flush_pools()
        self.set_exclude_info_maps_flag(exclude_info_maps)
        self.set_log_verbose(verbosity)
        self.set_metadata_prefix(output_prefix)
        self.create_directory(output_directory)
        if clear_output_directory:
            self.clear_output_dir(variables_file_path, output_directory)

        if chunkification:
            self.setup_pool_overflow_control(
                output_directory, max_memory_usage_percent, max_memory_usage, save_chunk_threshold_call_count
            )
        self.is_end_to_end_testing_run = is_end_to_end_testing_run

    def validate_filter_content(self, filters_dir_path: Path) -> None:
        """
        Validates the content of the filters, including keys and values.

        Parameters
        ----------
        filters_dir_path : Path
            Path of the directory containing the files containing the keys for filtering.

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.validate_filter_content.__name__,
        }
        list_of_filter_files = self._list_filter_files_in_dir(filters_dir_path)
        for filter_file in list_of_filter_files:
            input_path = filters_dir_path / filter_file
            filter_contents, direction = self._load_filter_file_content(input_path)
            if filter_file.endswith(".txt"):
                self.add_log(
                    "Filter validations skipped.", "Filter validation is not supported for" f"{filter_file}.", info_map
                )
                continue
            elif filter_file.startswith("graph_"):
                for filter_content in filter_contents:
                    self.validate_graph_details(filter_content, "graph_report", filter_file)
            elif filter_file.startswith("csv_"):
                for filter_content in filter_contents:
                    self.validate_csv_filters(filter_content, filter_file)
            elif filter_file.startswith("json_"):
                for filter_content in filter_contents:
                    self.validate_json_filters(filter_content, filter_file)
            else:
                for filter_content in filter_contents:
                    self.validate_report_filters(filter_content, filter_file)

    def validate_json_filters(self, filter_content: dict[Any, Any], filter_name: str) -> None:
        """
        Validate the json filter.

        Parameters
        ----------
        filter_content : dict[Any, Any]
            The report filter to validate.
        filter_name : str
            The name of the filter to validate.

        Returns
        -------
        None

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.validate_report_filters.__name__,
        }
        if not isinstance(filter_content, dict):
            self.add_error(
                "Parsing error",
                f"Could not validate {filter_name} must be a dictionary, it needs to be dictionary",
                info_map,
            )
            return

        key_validators: dict[str, Callable[[Any, Any, Any], None]] = {
            "name": partial(self.validate_type, expected=str, type_label="a string"),
            "filters": self.validate_list_of_strings,
            "variables": self.validate_list_of_strings,
        }

        if not isinstance(filter_content, dict) or "filters" not in filter_content.keys():
            self.add_error(
                "Parsing error",
                f"Could not parse {filter_content.get('name')=} in {filter_name},\
                    it has to have JSON blobs and have `filters` entry.",
                info_map,
            )
            return

        for key, value in filter_content.items():
            if key not in key_validators:
                self.add_error(
                    "Unknown key in json filter",
                    f"Key: {key}, is not a supported option for json filter {filter_content.get('name')=} in"
                    f" {filter_name}.",
                    info_map,
                )
                continue
            else:
                validator = key_validators[key]
                validator(value, key, filter_name)

    def validate_csv_filters(self, filter_content: dict[Any, Any], filter_name: str) -> None:
        """
        Validate the csv filter.

        Parameters
        ----------
        filter_content : dict[Any, Any]
            The report filter to validate.
        filter_name : str
            The name of the filter to validate.

        Returns
        -------
        None

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.validate_report_filters.__name__,
        }
        if not isinstance(filter_content, dict) or "filters" not in filter_content.keys():
            self.add_error(
                "Parsing error",
                f"Could not parse {filter_name},\
                    it has to have JSON blobs and have `filters` entry.",
                info_map,
            )
            return

        key_validators: dict[str, Callable[[Any, str, str], None]] = {
            "name": partial(self.validate_type, expected=str, type_label="a string"),
            "filters": self.validate_list_of_strings,
            "direction": self.validate_direction,
        }

        for key, value in filter_content.items():
            if key not in key_validators:
                self.add_error(
                    "Unknown key in csv filter",
                    f"Key: {key}, is not a supported option for csv filter {filter_content.get('name')=} in"
                    f" {filter_name}.",
                    info_map,
                )
                continue
            else:
                validator = key_validators[key]
                validator(value, key, filter_name)

    def validate_report_filters(self, filter_content: dict[Any, Any], filter_name: str) -> None:
        """
        Validate the report filter.

        Parameters
        ----------
        filter_content : dict[Any, Any]
            The report filter to validate.
        filter_name : str
            The name of the filter to validate.

        Returns
        -------
        None

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.validate_report_filters.__name__,
        }
        if not isinstance(filter_content, dict) or (
            "filters" not in filter_content.keys() and "cross_references" not in filter_content.keys()
        ):
            self.add_error(
                "Parsing error",
                f"Could not parse {filter_content.get('name')=} in {filter_name},\
                    it has to have JSON blobs and have `filters` entry."
                f"The `filters` can only be skipped if `cross_references` entry is present "
                f"and the purpose is to generate a derived report.",
                info_map,
            )
            return

        key_validators: dict[str, Callable[[Any, str, str], None]] = {
            "name": partial(self.validate_type, expected=str, type_label="a string"),
            "filters": self.validate_list_of_strings,
            "variables": self.validate_list_of_strings,
            "filter_by_exclusion": partial(self.validate_type, expected=bool, type_label="a boolean"),
            "constants": self.validate_dict_of_numbers,
            "cross_references": self.validate_list_of_strings,
            "vertical_aggregation": self.validate_aggregator,
            "horizontal_aggregation": self.validate_aggregator,
            "horizontal_first": partial(self.validate_type, expected=bool, type_label="a boolean"),
            "horizontal_order": self.validate_list_of_strings,
            "slice_start": partial(self.validate_type, expected=int, type_label="an integer"),
            "slice_end": partial(self.validate_type, expected=int, type_label="an integer"),
            "graph_and_report": partial(self.validate_type, expected=bool, type_label="a boolean"),
            "graph_details": self.validate_graph_details,
            "expand_data": partial(self.validate_type, expected=bool, type_label="a boolean"),
            "use_fill_value_in_gaps": partial(self.validate_type, expected=bool, type_label="a boolean"),
            "use_fill_value_at_end": partial(self.validate_type, expected=bool, type_label="a boolean"),
            "display_units": partial(self.validate_type, expected=bool, type_label="a boolean"),
            "simplify_units": partial(self.validate_type, expected=bool, type_label="a boolean"),
            "data_significant_digits": partial(self.validate_type, expected=int, type_label="an integer"),
            "direction": self.validate_direction,
            "use_name": partial(self.validate_type, expected=bool, type_label="a boolean"),
            "use_filter_key_name": partial(self.validate_type, expected=bool, type_label="a boolean"),
            "use_verbose_report_name": partial(self.validate_type, expected=bool, type_label="a boolean"),
        }

        for key, value in filter_content.items():
            if key == "fill_value":
                continue
            elif key not in key_validators:
                self.add_error(
                    "Unknown key in report filter",
                    f"Key: {key}, is not a supported option for filter {filter_content.get('name')=} in"
                    f" {filter_name}.",
                    info_map,
                )
                continue
            else:
                validator = key_validators[key]
                validator(value, key, filter_name)

    def validate_filter_constant_content(self, filters_dir_path: Path) -> None:
        """
        Validates the content of the filters, including keys and values.

        Parameters
        ----------
        filters_dir_path : Path
            Path of the directory containing the files containing the keys for filtering.

        """
        list_of_filter_files = self._list_filter_files_in_dir(filters_dir_path)
        for filter_file in list_of_filter_files:
            input_path = filters_dir_path / filter_file
            filter_contents, direction = self._load_filter_file_content(input_path)
            for content in filter_contents:
                for name, new_value in content.get("constants", {}).items():
                    if not hasattr(UserConstants, name):
                        continue
                    old_value = getattr(UserConstants, name)
                    if new_value == old_value:
                        continue

                    setattr(UserConstants, name, new_value)
                    self.add_warning(
                        "UserConstants overwritten.",
                        f"{name} overwritten by report filter; now set to {new_value}",
                        info_map={
                            "class": self.__class__.__name__,
                            "function": self.validate_filter_content.__name__,
                        },
                    )

    def validate_direction(self, value: Any, content_name: str, filter_name: str) -> None:
        """
        Validates the direction of CSV outputs.

        Parameters
        ----------
        value : Any
            The aggregator option to validate.
        content_name : str
            The corresponding filter option to provide in error reporting.
        filter_name : str
            Name of the filter to validate.
        Returns
        -------

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.validate_direction.__name__,
        }
        if value not in ["portrait", "landscape"]:
            self.add_error(
                "Invalid report direction.",
                f"[ERROR] '{content_name}' in {filter_name} " f"must be portrait or landscape.",
                info_map,
            )

    def validate_graph_details(self, value: Any, content_name: str, filter_name: str) -> None:
        """
        Validate the graph details provided.

        Parameters
        ----------
        value : Any
            The graph details to validate.
        content_name : str
            The corresponding filter option to provide in error reporting.
        filter_name : str
            Name of the filter to validate.

        Returns
        -------
        None

        """
        required_graph_filter_keys = ["type", "filters"]
        info_map = {
            "class": self.__class__.__name__,
            "function": self.validate_graph_details.__name__,
        }
        if not isinstance(value, dict):
            self.add_error(
                "Incorrect filter format.",
                f"'{content_name}' must be a dictionary format in {filter_name}.",
                info_map,
            )

        for required_key in required_graph_filter_keys:
            if required_key not in value.keys():
                self.add_error(
                    f"Can't plot {value.get('title')} data set",
                    f"Required key '{required_key}' not in {filter_name}.",
                    info_map,
                )

        key_validators: dict[str, Callable[[Any, str, str], None]] = {
            "type": self.validate_graph_type,
            "filters": self.validate_list_of_strings,
            "variables": self.validate_list_of_strings,
            "filter_by_exclusion": partial(self.validate_type, expected=bool, type_label="a boolean"),
            "customization_details": self.validate_customization_details,
            "legend": self.validate_list_of_strings,
            "display_units": partial(self.validate_type, expected=bool, type_label="a boolean"),
            "omit_legend_prefix": partial(self.validate_type, expected=bool, type_label="a boolean"),
            "omit_legend_suffix": partial(self.validate_type, expected=bool, type_label="a boolean"),
            "expand_data": partial(self.validate_type, expected=bool, type_label="a boolean"),
            "use_fill_value_in_gaps": partial(self.validate_type, expected=bool, type_label="a boolean"),
            "use_fill_value_at_end": partial(self.validate_type, expected=bool, type_label="a boolean"),
            "mask_values": partial(self.validate_type, expected=bool, type_label="a boolean"),
            "use_calendar_dates": partial(self.validate_type, expected=bool, type_label="a boolean"),
            "data_significant_digits": partial(self.validate_type, expected=int, type_label="an integer"),
            "title": partial(self.validate_type, expected=str, type_label="a string"),
            "slice_start": partial(self.validate_type, expected=int, type_label="an integer"),
            "slice_end": partial(self.validate_type, expected=int, type_label="an integer"),
        }

        for key, value in value.items():
            if key == "date_format":
                Utility.validate_date_format(value)
                continue
            if key == "fill_value":
                continue
            if key not in key_validators:
                self.add_error(
                    "Unknown key in graph details.",
                    f"Key: {key}, is not a supported option in {filter_name}.",
                    info_map,
                )
                continue
            key_validators[key](value, key, filter_name)

    def validate_type(self, value: Any, content_name: str, filter_name: str, expected: type, type_label: str) -> None:
        """
        Generic type checker.

        Parameters
        ----------
        value : Any
            The value to check.
        content_name : str
            Name of the field, for error messages.
        filter_name: str
            Name of the filter validated.
        expected : type
            A type or tuple of types that value must be an instance of.
        type_label : str
            A human-readable description of the type (used in the error message).
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.validate_type.__name__,
        }
        if not isinstance(value, expected):
            content_type = type(value)
            self.add_error(
                "Invalid report filter data type",
                f"[ERROR] '{content_name}' in {filter_name} " f"must be {type_label} but received {content_type}.",
                info_map,
            )

    def validate_aggregator(self, value: Any, content_name: str, filter_name: str) -> None:
        """
        Validate the aggregator option provided.

        Parameters
        ----------
        value : Any
            The aggregator option to validate.
        content_name : str
            The corresponding filter option to provide in error reporting.
        filter_name : str
            Name of the filter to validate.

        Returns
        -------
        None

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.validate_aggregator.__name__,
        }
        self.validate_type(value, content_name, filter_name, expected=str, type_label="a string")

        supported = {
            "average",
            "division",
            "product",
            "SD",
            "sum",
            "subtraction",
        }
        if value not in supported:
            self.add_error(
                "Unsupported aggregator in report filter content",
                f"[ERROR] '{content_name}' in {filter_name} must be one of {sorted(supported)}, but got '{value}'.",
                info_map,
            )
            raise ValueError(
                f"[ERROR] '{content_name}' in {filter_name} must be one of {sorted(supported)}, but got '{value}'."
            )

    def validate_list_of_strings(self, value: Any, content_name: str, filter_name: str) -> None:
        """
        Validate filter content that should be list of strings.

        Parameters
        ----------
        value : Any
            The filter content to validate.
        filter_name : str
            The name of the filter to validate.
        content_name : str
            The corresponding filter option to provide in error reporting.

        Returns
        -------
        None

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.validate_list_of_strings.__name__,
        }
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            self.add_error(
                "Invalid report filter data type",
                f"[ERROR] '{content_name}' in {filter_name} must be a list of strings.",
                info_map,
            )

    def validate_dict_of_numbers(self, value: Any, content_name: str, filter_name: str) -> None:
        """
        Validate filter content that should be a dictionary with string type as keys and int or float as values.

        Parameters
        ----------
        value : Any
            The filter content to validate.
        content_name : str
            The corresponding filter option to provide in error reporting.
        filter_name : str
            Name of the filter to validate.

        Returns
        -------
        None

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.validate_dict_of_numbers.__name__,
        }
        if not isinstance(value, dict) or not all(
            isinstance(k, str) and isinstance(v, (int, float)) for k, v in value.items()
        ):
            self.add_error(
                "Invalid report filter data type",
                f"[ERROR] '{content_name}' in {filter_name} must be a dictionary with"
                f" numeric values (int or float).",
                info_map,
            )

    def validate_graph_type(self, value: Any, content_name: str, filter_name: str) -> None:
        """
        Validate the provided graph type in the filter contents.

        Parameters
        ----------
        value : Any
            The filter content to validate.
        content_name : str
            The corresponding filter option to provide in error reporting.
        filter_name : str
            Name of the filter to validate.

        Returns
        -------
        None

        """
        self.validate_type(value, content_name, filter_name, expected=str, type_label="a string")
        info_map = {
            "class": self.__class__.__name__,
            "function": self.validate_graph_type.__name__,
        }
        allowed = {
            "barbs",
            "boxplot",
            "hexbin",
            "histogram",
            "pie",
            "plot",
            "polar",
            "quiver",
            "scatter",
            "spy",
            "stackplot",
            "stem",
            "violin",
        }
        if value not in allowed:
            self.add_error(
                "Unsupported graph type",
                f"[ERROR] '{content_name}' in {filter_name} must be one of {sorted(allowed)}, but got '{value}'.",
                info_map,
            )

    def validate_customization_details(self, value: Any, content_name: str, filter_name: str) -> None:
        """
        Validate the graph customization details in the filter contents.

        Parameters
        ----------
        value : Any
            The filter content to validate.
        content_name : str
            The corresponding filter option to provide in error reporting.
        filter_name : str
            Name of the filter to validate.

        Returns
        -------
        None

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.validate_customization_details.__name__,
        }
        allowed = {
            "align_labels",
            "aspect",
            "canvas",
            "constrained_layout",
            "dpi",
            "edgecolor",
            "facecolor",
            "figheight",
            "figsize",
            "figwidth",
            "frameon",
            "grid",
            "legend",
            "snap",
            "subplot_adjust",
            "tight_layout",
            "title",
            "transform",
            "xlabel",
            "xticklabels",
            "xticks",
            "xlim",
            "ylabel",
            "yticklabels",
            "yticks",
            "ylim",
            "yscale",
            "xscale",
            "zorder",
        }
        if not isinstance(value, dict):
            content_type = type(value)
            self.add_error(
                "Unsupported customization option type",
                f"[ERROR] '{content_name}' in {filter_name} must be a dict of customization options, but received "
                f"{content_type}.",
                info_map,
            )
            return None
        for opt in value:
            if opt not in allowed:
                self.add_error(
                    "Unsupported customization option",
                    f"[ERROR] Unknown customization option '{opt}' in '{content_name}' of {filter_name}.",
                    info_map,
                )

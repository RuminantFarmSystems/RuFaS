# !/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy
from enum import Enum
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Union
import datetime
import json
import os
import pandas as pd
import re
from deprecated.sphinx import deprecated

from RUFAS.util import Utility
from RUFAS.graph_generator import GraphGenerator
from RUFAS.report_generator import ReportGenerator


class LogVerbosity(Enum):
    """
    The different types of logs printed by Output Manager. Set by the `verbose` gnu arg in main.py.

    Notes
    -----
    NONE is the default setting.
    Selecting NONE will tell OutputManager not to print out anything during a simulation.
    Selecting ERRORS will tell OutputManager to print out all errors added during a simulation.
    Selecting WARNINGS will tell OutputManager to print out all warnings and errors added during a simulation.
    Selecting LOGS will tell OutputManager to print out all logs, warnings, and errors added during a simulation.
    """

    NONE = "none"
    ERRORS = "errors"
    WARNINGS = "warnings"
    LOGS = "logs"

    def __le__(self, other) -> bool:
        if self == other:
            return True
        if self == LogVerbosity.NONE:
            return True
        if self == LogVerbosity.ERRORS and other != LogVerbosity.NONE:
            return True
        if self == LogVerbosity.WARNINGS and other == LogVerbosity.LOGS:
            return True
        if self == LogVerbosity.LOGS:
            return False
        return False

    def __str__(self) -> bool:
        if self.value == "none":
            return "NONE"
        return self.value[:-1].upper()


class OutputManager(object):
    """
    Output manager for RuFaS simulation results. Works by collecting variables,
    logs, warnings, and errors into separate pools, and populates requested
    output channels from the pools once the simulation is done.

    OutputManager is singleton, i.e., only one instance of it can exist. After
    the first instance is created, future calls to the constructor method
    returns the first instance. Also, the initializer method only works once.

    Attributes
    ----------
    variables_pool : Dict[str, Dict[str, List[Dict[str, Any]]]
        Contains variables reported to the output manager
    warnings_pool : Dict[str, Dict[str, List[Dict[str, Any]]]
        Contains warnings reported to the output manager
    errors_pool : Dict[str, Dict[str, List[Dict[str, Any]]]
        Contains errors reported to the output manager
    logs_pool : Dict[str, Dict[str, List[Dict[str, Any]]]
        Contains logs reported to the output manager
    """

    __instance = None
    pool_element_type = Dict[str, List[Any]]

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(OutputManager, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        if OutputManager.__instance is None:
            OutputManager.__instance = self
            self.variables_pool: Dict[str, OutputManager.pool_element_type] = {}
            self.warnings_pool: Dict[str, OutputManager.pool_element_type] = {}
            self.errors_pool: Dict[str, OutputManager.pool_element_type] = {}
            self.logs_pool: Dict[str, OutputManager.pool_element_type] = {}
            self.__metadata_prefix: str = ""
            self.__supported_filter_types_prefixes: Dict[str, str] = {
                "csv": "csv_",
                "graph": "graph_",
                "json": "json_",
                "report": "report_",
            }
            self.__log_verbose: LogVerbosity = LogVerbosity("none")
            self.add_log(
                "init_log",
                "Output Manager instantiated.",
                info_map={
                    "class": self.__class__.__name__,
                    "function": self.__init__.__name__,
                },
            )

    def _pool_element_factory(self) -> pool_element_type:
        """Factory for elements added to pools"""
        info_maps: List[Dict[str, Any]] = []
        values: List[Any] = []
        return {"info_maps": info_maps, "values": values}

    def _add_to_pool(
            self,
            pool: Dict[str, pool_element_type],
            key: str,
            value: Any,
            info_map: Dict[str, Any],
    ) -> None:
        """Adds value and info map at key in the given pool."""
        key_not_exists_in_pool = pool.get(key) is None
        if key_not_exists_in_pool:
            pool[key] = self._pool_element_factory()
        # reduced_info_map is identical to info_map without the class key and
        # the function key; as they are already stored in element key and
        # having them increases the final file size.
        reduced_info_map = {
            k: info_map[k]
            for k in info_map.keys() - {"class", "function"}
        }
        pool[key]["info_maps"].append(reduced_info_map)

        if isinstance(value, (int, bool, float, str)):
            pool[key]["values"].append(value)
        else:
            pool[key]["values"].append(deepcopy(value))

    def add_variable(self, name: str, value: Any, info_map: Dict[str, Any]) -> None:
        """
        Adds a variable to the pool.

        Parameters
        ----------
        name : str
            The name of the variable
        value : Any
            The value of the variable
        info_map : Dict[str, Any]
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
        """
        key = self._generate_key(name, info_map)
        self._add_to_pool(self.variables_pool, key, value, info_map)

    def add_log(self, name: str, msg: str, info_map: Dict[str, Any]) -> None:
        """
        Adds a log message to the pool of logs.

        Parameters
        ----------
        name : str
            The name of the log
        msg : str
            The log message to be added to the pool
        info_map: Dict[str, Any]
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
        info_map["timestamp"] = self._get_timestamp(include_millis=True)
        key = self._generate_key(name, info_map)
        self._add_to_pool(self.logs_pool, key, msg, info_map)
        self._handle_log_output(name, msg, info_map, LogVerbosity.LOGS)

    def add_warning(self, name: str, msg: str, info_map: Dict[str, Any]) -> None:
        """
        Adds a warning message to the pool of warnings.

        Parameters
        ----------
        name : str
            The name of the warning
        msg : str
            The warning message to be added to the pool
        info_map: Dict[str, Any]
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
        info_map["timestamp"] = self._get_timestamp(include_millis=True)
        key = self._generate_key(name, info_map)
        self._add_to_pool(self.warnings_pool, key, msg, info_map)
        self._handle_log_output(name, msg, info_map, LogVerbosity.WARNINGS)

    def add_error(self, name: str, msg: str, info_map: Dict[str, Any]) -> None:
        """
        Adds an error message to the pool of errors.

        Parameters
        ----------
        name : str
            The name of the error
        msg : str
            The error message to be added to the pool
        info_map: Dict[str, Any]
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
        info_map["timestamp"] = self._get_timestamp(include_millis=True)
        key = self._generate_key(name, info_map)
        self._add_to_pool(self.errors_pool, key, msg, info_map)
        self._handle_log_output(name, msg, info_map, LogVerbosity.ERRORS)

    def _handle_log_output(
            self, name: str, msg: str, info_map: Dict[str, Any], log_level: LogVerbosity
    ) -> None:
        """Formats log output based on log_level.

        Parameters
        ----------
        name : str
            The name of the log.
        msg : str
            The log message to be added to the pool.
        info_map : Dict[str, Any]
            Additional args to be logged.
        log_level : LogVerbosity
            The LogVerbosity level.
        """
        colors: Dict[LogVerbosity, str] = {
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

    def set_log_verbose(self, log_verbose: LogVerbosity = LogVerbosity.NONE) -> None:
        """Sets the __log_verbose attribute"""
        self.__log_verbose = log_verbose

    def _get_timestamp(self, include_millis: bool = False) -> str:
        """
        Produces the current system time as a timestamp string.

        Parameters
        ----------
        include_millis : bool
            If True, adds milliseconds to the timestamp.

        Returns
        -------
        str
            The current time's timestamp string.

        Example
        --------
        >>> self._get_timestamp(include_millis=True)
        28-Jun-2023_Wed_15-48-21.406585
        >>> self._get_timestamp(include_millis=False)
        28-Jun-2023_Wed_15-48-21
        """
        base_timestamp_str: str = "%d-%b-%Y_%a_%H-%M-%S"
        timestamp_format_string: str = (
            f"{base_timestamp_str}.%f" if include_millis else base_timestamp_str
        )
        return datetime.datetime.now().strftime(timestamp_format_string)

    def _generate_key(self, name: str, info_map: Dict[str, Union[str, bool]]) -> str:
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
        if info_map.get("prefix") is not None:
            prefix = info_map.get("prefix") + "."
        elif not info_map.get("suppress_prefix", False):
            prefix = (
                    self._get_prefix(info_map.get("class"), info_map.get("function")) + "."
            )

        suffix = (
            f'.{info_map.get("suffix")}' if info_map.get("suffix") is not None else ""
        )

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

    def dict_to_file_json(self, data_dict: Dict[str, Any], path: str, minify_output_file: bool = False) -> None:
        """Saves a dictionary into a JSON file

        Parameters
        ----------
        data_dict : Dict[str, Any]
            The dictionary to be saved

        path : str
            The path to the file to be saved

        minify_output_file : bool
            Boolean flag indicating whether to minify the output JSON file.

        Raises
        ------
        Exception
            If an error occurs while saving to the file

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
        try:
            with open(path, "w") as json_file:
                if minify_output_file:
                    json.dump(
                        Utility.make_serializable(data_dict, max_depth=3),
                        json_file,
                        separators=(",", ":")
                    )
                else:
                    json.dump(
                        Utility.make_serializable(data_dict, max_depth=3),
                        json_file,
                        indent=2,
                    )
                self.add_log(
                    "save_dict_file_success", f"Successfully saved to {path}.", info_map
                )
        except Exception as e:
            raise e

    def _dict_to_csv_column_list(
            self, variable_name: str, data_dict: Dict[str, List[Any]]
    ) -> List[pd.Series]:
        """Turns a dictionary to a list of csv columns.

        Parameters
        ----------
        variable_name : str
            The name of the variable having its values written into a CSV column.
        data_dict : Dict[str, List[Any]]
            The dictionary to read from

        Returns
        -------
        List[pd.Series]
            A list of (column_name, column_data) tuples.

        """
        column_list = []
        mandatory_fields = (
            ["values", "info_maps"] if "info_maps" in data_dict else ["values"]
        )
        for field in mandatory_fields:
            data_list = data_dict[field]
            if data_list and isinstance(data_list[0], dict):
                csv_column_lists: Dict[str, List[Any]] = {
                    subkey: [] for item in data_list for subkey in item.keys()
                }
                for nested_dictionary in data_list:
                    for subkey, value in nested_dictionary.items():
                        csv_column_lists[subkey].append(value)

                for subkey in csv_column_lists.keys():
                    column_title = f"{variable_name}.{subkey}"
                    column_list.append(
                        pd.Series(
                            csv_column_lists[subkey], dtype=object, name=column_title
                        )
                    )
            else:
                column_title = f"{variable_name}"
                column_list.append(
                    pd.Series(data_list, dtype=object, name=column_title)
                )

        return column_list

    def _dict_to_file_csv(self, data_dict: Dict[str, Any], path: str) -> None:
        """Saves a dictionary to a csv file.

        Parameters
        ----------
        data_dict : Dict[str, Any]
            The dictionary to be saved.
        path : str
            The path to the file to be saved.

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
            csv_column_data = self._dict_to_csv_column_list(
                variable_name, variable_data
            )
            csv_columns.extend(csv_column_data)

        df = pd.concat(csv_columns, axis=1)

        df.to_csv(path, index=False)

        self.add_log("save_dict_file_try", f"Successfully saved to {path}.", info_map)

    def _list_to_file_txt(self, data_list: List[str], path: str) -> None:
        """Saves a list into a text file

        Parameters
        ----------
        data_list : List[str]
            The list of variable names to be saved
        path : str
            The path to the file to be saved

        Raises
        ------
        Exception
            If an error occurs while saving to the file
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._list_to_file_txt.__name__,
        }
        self.add_log("save_txt_file_try", f"Attempting to save to {path}.", info_map)
        try:
            with open(path, "w") as var_names_file:
                var_names_file.writelines(data_list)
                self.add_log(
                    "save_txt_file_success", f"Successfully saved to {path}.", info_map
                )
        except Exception as e:
            raise e

    def _generate_file_name(self, base_name: str, extension: str) -> str:
        """
        Returns a file name using the given base_name and timestamp.
        """
        timestamp: str = self._get_timestamp(include_millis=False)
        return f"{self.__metadata_prefix}_{base_name}_{timestamp}.{extension}"

    def _exclude_info_maps(
            self, pool: Dict[str, pool_element_type]
    ) -> Dict[str, pool_element_type]:
        """Makes a copy of the given pool and removes info_maps from it.

        Returns
        -------
        Dict[str, OutputManager.pool_element_type]
            A copy of the given pool with info_maps removed from it.

        """
        pool_copy = pool.copy()
        for key, value in pool_copy.items():
            if isinstance(value, dict) and "info_maps" in value:
                value.pop("info_maps")
        return pool_copy

    def _list_filter_files_in_dir(self, dir_path: str) -> List[str]:
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
        dir_path_check = Path(dir_path)
        if dir_path_check.is_dir():
            filter_files = []
            all_files = os.listdir(dir_path)
            for filename in all_files:
                if filename.endswith(".txt") or filename.endswith(".json"):
                    for (
                            _,
                            supported_prefix,
                    ) in self.__supported_filter_types_prefixes.items():
                        if filename.startswith(supported_prefix):
                            break
                    else:
                        self.add_warning(
                            "invalid filter file prefix",
                            f"{filename} prefix is not in {list(self.__supported_filter_types_prefixes.values())}",
                            info_map,
                        )
                        continue
                    filter_files.append(filename)
            self.add_log(
                "search_path_for_filenames_success",
                f"Successfully searched in {dir_path}"
                f" and found {len(filter_files)} filter files.",
                info_map,
            )
            return filter_files
        else:
            raise NotADirectoryError("The specified path must be a directory")

    def _load_filter_file_content(self, path: str) -> List[Dict[str, str | int]]:
        """
        Loads and processes the content of a filter file from the specified path.

        Parameters
        ----------
        path : str
            The path to the filter file (either .json or .txt).

        Returns
        -------
        List[Dict[str, str|int]]
            A list of dictionaries, each containing the loaded filter content,
            with keys and values depending on the file type.

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
                if path.endswith(".json"):
                    json_content = json.load(filter_file)
                    if "multiple" in json_content.keys():
                        result = json_content["multiple"]
                    else:
                        result = [json_content]
                elif path.endswith(".txt"):
                    list_of_elements = [
                        element
                        for element in filter_file.read().splitlines()
                        if element
                    ]
                    result = [{"filters": list_of_elements}]
                else:
                    raise Exception(
                        "Unsupported file format; only json and txt are supported."
                    )
            self.add_log("text_file_load_log", f"Successfully opened {path}.", info_map)
            return result
        except FileNotFoundError:
            self.add_error(
                "File not found", f"The file '{path}' does not exist.", info_map
            )
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

    def _filter_variables_pool(
            self, filter_patterns: List[str], input_file_name: Optional[str]
    ) -> Dict[str, pool_element_type]:
        """
        Returns a filtered variables pool based on either inclusion or exclusion.

        Parameters
        ----------
        filter_patterns : List[str]
            A list of patterns the user has selected to filter the variables pool.

        input_file_name : str, optional
            The filter patterns file name - necessary for logging purposes

        Returns
        -------
        Dict[str, OutputManager.pool_element_type]
            A filtered variables pool based on either inclusion or exclusion.

        Notes
        -----
        The first item in the filter_patterns list will determine whether the patterns are treated as
        exclusionary or inclusionary. If the first pattern matches the value of the exclude_keyword
        variable defined in this function, it will treat the rest of the filter list as exclusionary
        and filter the variables_pool accordingly. Otherwise, it will treat the list of filters
        as inclusionary.

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._filter_variables_pool.__name__,
        }
        exclude_keyword_location = 0
        exclude_keyword = "exclude"
        filter_by_exclusion = (
                filter_patterns
                and filter_patterns[exclude_keyword_location] == exclude_keyword
        )
        if filter_by_exclusion:
            filter_vars_msg = (
                f"{input_file_name} has exclude-keyword '{exclude_keyword}' at"
                f" position {exclude_keyword_location}. Performing filtering by exclusion."
            )
            filter_pattern_matches = {
                key: self.variables_pool[key]
                for key in self.variables_pool.keys()
                if not any(re.match(pattern, key) for pattern in filter_patterns)
            }
        else:
            filter_vars_msg = (
                f"{input_file_name} does NOT contain exclude-keyword '{exclude_keyword}'"
                f" at position {exclude_keyword_location}. Performing filtering by inclusion."
            )
            filter_pattern_matches = {
                key: self.variables_pool[key]
                for key in self.variables_pool.keys()
                if any(re.match(pattern, key) for pattern in filter_patterns)
            }
        self.add_log("filtering_log", filter_vars_msg, info_map)
        filter_log_count_msg = (
            f"There were {len(filter_pattern_matches)} matches for the {len(filter_patterns)}"
            f" filter pattern(s) in the {input_file_name} file."
        )
        self.add_log("num_filter_pattern_matches", filter_log_count_msg, info_map)
        return filter_pattern_matches

    def save_results(
            self,
            save_path: Path,
            filters_dir_path: Path,
            exclude_info_maps: bool,
            produce_graphics: bool,
            graphics_dir: Path,
            csv_dir: Path
    ) -> None:
        """
        Reads a text file containing a list of keys and filters the variables pool by those keys.
        Saves resulting data pool to a json file in the given path to a directory.

        Parameters
        ----------
        save_path : Path
            Path to the directory where the file will be saved.

        filters_dir_path : Path
            Path of the directory containing the files containing the keys for filtering.

        exclude_info_maps : bool
            Flag for whether or not the user wants to include info_maps data in their results files.

        produce_graphics: bool
            Flag for whether or not the user wants to produce graphs at after the simulation.

        graphics_dir : Path
            The directory for saving graphics.

        csv_dir : Path
            The directory for saving csvs.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.save_results.__name__,
        }
        self.add_log(
            "exclude_info_maps",
            f"exclude_info_maps flag set to {exclude_info_maps}",
            info_map,
        )
        list_of_filter_files = self._list_filter_files_in_dir(filters_dir_path)
        for filter_file in list_of_filter_files:
            info_map["filter file"] = filter_file
            input_path = os.path.join(filters_dir_path, filter_file)
            filter_contents = self._load_filter_file_content(input_path)
            reports: Dict[str: Dict[str: List[Any]]] = {}
            for filter_content in filter_contents:
                info_map["filter_content"] = filter_content
                if (
                        not isinstance(filter_content, dict)
                        or ("filters" not in filter_content.keys() and "cross_references" not in filter_content.keys())
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

                filtered_pool:  Dict[str, Dict[str, List[Any]]] = {}
                if "filters" in filter_content.keys():
                    filtered_pool = self._filter_variables_pool(
                        filter_content["filters"], filter_file
                    )
                if exclude_info_maps:
                    filtered_pool = self._exclude_info_maps(filtered_pool)

                if filter_file.startswith(
                        self.__supported_filter_types_prefixes["report"]
                ):
                    self._handle_report_generation(filter_content, filtered_pool, info_map, reports)
                else:
                    self._route_save_functions(
                        filter_file,
                        save_path,
                        filtered_pool,
                        produce_graphics,
                        filter_content,
                        graphics_dir,
                        csv_dir,
                    )
            report_file_path = os.path.join(
                save_path,
                self._generate_file_name(f"report_{filter_file}", "csv"),
            )
            self._dict_to_file_csv(reports, report_file_path)

    def _handle_report_generation(self,
                                  filter_content: Dict[str, Any],
                                  filtered_pool: Dict[str, Dict[str, List[Any]]],
                                  info_map: Dict[str, Any],
                                  reports: Dict[str, Dict[str, List[Any]]]) -> None:
        """
        Handles the generation of reports based on the provided filter content.

        Notes
        -----
        If the report name is not unique, the timestamp is appended to the name to make it unique.

        Any errors that occur during report generation are logged and the report is skipped.

        The following are a few examples of errors that can occur during report generation:
        - There are no data points to aggregate.

        - There are any cross-references that are missing.

        - Neither horizontal nor vertical aggregation is specified.

        - The aggregation type is not supported. The supported aggregation types are: sum, average, product,
        subtraction, division, SD (standard deviation).

        Parameters
        ----------
        filter_content : Dict[str, Any]
            A dictionary containing the configuration for the report, including details
            such as 'name', 'filters', 'cross_references', and aggregation instructions.

        filtered_pool : Dict[str, Dict[str, List[Any]]]
            The data pool from which reports are generated.

        info_map : Dict[str, Any]
            A dictionary containing logging information such as the class and function names.

        reports : Dict[str, Dict[str, List[Any]]]
            A dictionary to store the generated reports, keyed by their names.
        """

        self.add_log("init_report_generation", "Report Generation Started", info_map)
        report_generator = ReportGenerator()
        try:
            report_name = self._generate_unique_report_name(filter_content, reports)

            if "cross_references" in filter_content.keys():
                self._check_for_missing_references(filter_content["cross_references"], reports)
                cross_reference_data = {ref: reports[ref] for ref in filter_content["cross_references"]}
                filtered_pool.update(cross_reference_data)

            report_data = report_generator.generate_aggregate_report(filtered_pool, filter_content)

            reports[report_name] = {"values": report_data}

        except (ValueError, KeyError) as e:
            self.add_error("report generation error", str(e), info_map)

    def _generate_unique_report_name(self, filter_content: Dict[str, Any], reports: Dict[str, Any]) -> str:
        """
        Generates a unique name for the report.

        Parameters
        ----------
        filter_content : Dict[str, Any]
            The filter content for the report.
        reports : Dict[str, Any]
            The dictionary of reports to check against.

        Returns
        -------
        str
            The unique name for the report.
        """

        base_name = filter_content.get("name", f"untitled_{self._get_timestamp(True)}")

        if base_name in reports:
            base_name = f"{base_name} {self._get_timestamp(True)}"

        return base_name

    @staticmethod
    def _check_for_missing_references(references: List[str], reports: Dict[str, Any]) -> None:
        """
        Checks if all the referenced reports are present.

        Parameters
        ----------
        references : List[str]
            The list of references to check.
        reports : Dict[str, Any]
            The dictionary of reports to check against.

        Raises
        ------
        KeyError
            If any of the references are missing.
        """

        missing_references = [ref for ref in references if ref not in reports]
        if missing_references:
            raise KeyError(f"Missing referenced reports: {', '.join(missing_references)}")

    def _route_save_functions(
            self,
            filter_file: str,
            save_path: Path,
            filtered_pool: Dict[str, pool_element_type],
            produce_graphics: bool,
            filter_content: Dict[str, str | int],
            graphics_dir: Path,
            csv_dir: Path
    ) -> None:
        """
        Checks the prefix of the filter_file to determine the format for saving. It then delegates the
        saving process to the corresponding function to handle specific formats such as JSON, CSV, or graphical output.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._route_save_functions.__name__,
        }
        if filter_file.startswith(self.__supported_filter_types_prefixes["json"]):
            file_path = os.path.join(
                save_path,
                self._generate_file_name(f"saved_variables_{filter_file}", "json"),
            )
            self.dict_to_file_json(filtered_pool, file_path)
        elif filter_file.startswith(self.__supported_filter_types_prefixes["csv"]):
            self.create_directory(csv_dir)
            variable_csv_file_path = os.path.join(
                csv_dir,
                self._generate_file_name(f"saved_variables_{filter_file}", "csv"),
            )
            self._dict_to_file_csv(filtered_pool, variable_csv_file_path)
        elif filter_file.startswith(self.__supported_filter_types_prefixes["graph"]):
            self.create_directory(graphics_dir)
            if produce_graphics:
                try:
                    graph_generator = GraphGenerator(self.__metadata_prefix)
                    log_pool = graph_generator.generate_graph(
                                filtered_pool,
                                filter_content,
                                filter_file,
                                graphics_dir,
                                )
                    self._route_logs(log_pool)
                except Exception as e:
                    self.add_error("graph generation exception", str(e), info_map)
            else:
                self.add_warning(
                    "No Graphics",
                    f"Graphic generation is disabled, skipping {filter_file=}",
                    info_map,
                )

    def _route_logs(self, log_pool: List[Dict[str, str | Dict[str, str]]]) -> None:
        """Takes logs from other classes and routes them to the appropriate pools in
        Output Manager.

        Parameters
        ----------
        log_pool : List[Dict[str, str | Dict[str, str]]]
            A list of log, warning, and error dictionaries containing all the components needed
            to log the information to the appropriate pool.
        """
        for log in log_pool:
            if "error" in log:
                self.add_error(log["error"], log["message"], log["info_map"])
            elif "log" in log:
                self.add_log(log["log"], log["message"], log["info_map"])
            elif "warning" in log:
                self.add_warning(log["warning"], log["message"], log["info_map"])

    @deprecated(
        reason="""This function is still in the code base but it is not used. We want to keep it for debugging purposes
        when save_results() is not working.""",
        version="MVP",
    )
    def dump_variables(self, path: str, exclude_info_maps: bool) -> None:
        """
        Dumps variables_pool into a json file in the given path to a directory.

        Parameters
        ----------
        path : str
            Path to the directory where the file will be saved.

        exclude_info_maps : bool
            Flag for whether or not the user wants to inlcude info_maps data in their results files.

        """
        pool = self.variables_pool
        if exclude_info_maps:
            pool = self._exclude_info_maps(self.variables_pool)

        json_file_path = os.path.join(
            path, self._generate_file_name("all_variables", "json")
        )
        self.dict_to_file_json(pool, json_file_path)

    def dump_logs(self, path: str) -> None:
        """
        Dumps logs_pool into a json file in the given path to a directory.
        """
        file_path = os.path.join(path, self._generate_file_name("logs", "json"))
        self.dict_to_file_json(self.logs_pool, file_path)

    def dump_warnings(self, path: str) -> None:
        """
        Dumps warnings_pool into a json file in the given path to a directory.
        """
        file_path = os.path.join(path, self._generate_file_name("warnings", "json"))
        self.dict_to_file_json(self.warnings_pool, file_path)

    def dump_errors(self, path: str) -> None:
        """
        Dumps errors_pool into a json file in the given path to a directory.
        """
        file_path = os.path.join(path, self._generate_file_name("errors", "json"))
        self.dict_to_file_json(self.errors_pool, file_path)

    def dump_variable_names_and_contexts(  # noqa: C901
            self,
            path: str,
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
        for name, variable_data in self.variables_pool.items():
            if "values" not in variable_data:
                var_list.append(f"{name}: **NO VARIABLES**{os.linesep}")
                continue

            parsable_dicts = []

            if not exclude_info_maps:
                parsable_dicts.append("info_maps")

            is_variable_nested = isinstance(variable_data["values"][0], Dict)
            if is_variable_nested:
                parsable_dicts.append("values")
            else:
                var_list.append(f"{name}{os.linesep}")

            prefix = name
            if format_option == "block":
                if f"{name}{os.linesep}" not in var_list:
                    var_list.append(f"{name}{os.linesep}")
                prefix = " " * len(name)

            for parsable_dict in parsable_dicts:
                keys = variable_data[parsable_dict][0].keys()
                if format_option == "inline":
                    var_list.append(f"{name}.{parsable_dict}: {list(keys)}{os.linesep}")
                elif format_option == "basic":
                    for key in keys:
                        var_list.append(f"{name}.{key}{os.linesep}")
                else:
                    for key in keys:
                        var_list.append(f"{prefix}.{parsable_dict}: {key}{os.linesep}")

        file_path = os.path.join(
            path, self._generate_file_name("variable_names", "txt")
        )
        self._list_to_file_txt(var_list, file_path)

    def dump_all_nondata_pools(
            self,
            path: str,
            exclude_info_maps: bool,
            format_option: str,
    ) -> None:
        """
        Dumps all non-data pools into the given path to a directory.
        """
        self.dump_variable_names_and_contexts(path, exclude_info_maps, format_option)
        self.dump_logs(path)
        self.dump_warnings(path)
        self.dump_errors(path)

    def flush_pools(self) -> None:
        """
        Sets each pool to an empty dictionary.
        """
        self.variables_pool: Dict[str, OutputManager.pool_element_type] = {}
        self.warnings_pool: Dict[str, OutputManager.pool_element_type] = {}
        self.errors_pool: Dict[str, OutputManager.pool_element_type] = {}
        self.logs_pool: Dict[str, OutputManager.pool_element_type] = {}

    def load_variables_pool_from_file(self, file_path: Path) -> None:
        """Loads the Output Manager variables pool from file path provided by user.

        Parameters
        ----------
        file_path : Path
            The path to the file to be loaded to the variables pool.

        Raises
        ------
        Exception
            If an error occurs while opening or reading the user-provided file path.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.load_variables_pool_from_file.__name__,
        }
        self.add_log(
            "open_json_file", f"Attempting to open {str(file_path)}.", info_map
        )
        try:
            with open(file_path) as file:
                self.variables_pool = json.load(file)
                self.add_log(
                    "load_data_successful",
                    f"Successfully loaded data from {str(file_path)}.",
                    info_map,
                )
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
            self.add_error(
                "Permission Error", f"{path=}; Exception: {str(e)}", info_map
            )
        except Exception as e:
            self.add_error("mkdir failure", f"{path=}; Exception: {str(e)}", info_map)

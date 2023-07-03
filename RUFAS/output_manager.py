# !/usr/bin/env python3

from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Union
import json
import os
import datetime

from RUFAS.util import Utility


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
    pool_element_type = Dict[str, List[Dict[str, Any]]]

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
            k: info_map[k] for k in info_map.keys() - {"class", "function"}
        }
        pool[key]["info_maps"].append(reduced_info_map)
        pool[key]["values"].append(value)

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
            The current time's timestamp string in the form.

        Example
        --------
        >>> self._get_timestamp(include_millis=True)
        28-Jun-2023_Wed_15-48-21.406585
        >>> self._get_timestamp(include_millis=False)
        28-Jun-2023_Wed_15-48-21
        """
        base_timestamp_str: str = "%d-%b-%Y_%a_%H-%M-%S"
        timestamp_format_string: str = f"{base_timestamp_str}.%f" if include_millis else base_timestamp_str
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

    def _dict_to_file_json(self, data_dict: Dict[str, Any], path: str) -> None:
        """Saves a dictionary into a JSON file

        Parameters
        ----------
        data_dict : Dict[str, Any]
            The dictionary to be saved
        path : str
            The path to the file to be saved

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
        serialized dictionary using the max_depth parameter.

        """
        info_map = {"class": self.__class__.__name__,
                    "function": self._dict_to_file_json.__name__,
                    }
        self.add_log("save_dict_file_try", f"Attempting to save to {path}.", info_map)
        try:
            with open(path, "w") as json_file:
                json.dump(
                    Utility.make_serializable(data_dict, max_depth=3),
                    json_file,
                    indent=0,
                )
                self.add_log("save_dict_file_success", f"Successfully saved to {path}.", info_map)
        except Exception as e:
            raise e

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
        info_map = {"class": self.__class__.__name__,
                    "function": self._list_to_file_txt.__name__,
                    }
        self.add_log("save_txt_file_try", f"Attempting to save to {path}.", info_map)
        try:
            with open(path, "w") as var_names_file:
                var_names_file.writelines(data_list)
                self.add_log("save_txt_file_success", f"Successfully saved to {path}.", info_map)
        except Exception as e:
            raise e

    def _generate_file_name(self, base_name: str, extension: str = "json") -> str:
        """
        Returns a file name using the given base_name and timestamp.
        """
        timestamp: str = self._get_timestamp(include_millis=False)
        return f"{base_name}_{timestamp}.{extension}"

    def _exclude_info_maps(self, pool: Dict[str, pool_element_type]) -> Dict[str, pool_element_type]:
        """ Makes a copy of the given pool and removes info_maps from it.

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

    def _list_txt_file_names_in_dir(self, dir_path: str) -> List[str]:
        """ Returns the list of files in the given path"""
        info_map = {"class": self.__class__.__name__,
                    "function": self._list_txt_file_names_in_dir.__name__,
                    }
        self.add_log("search_path_for_filenames_try", f"Attempting to search in {dir_path}.", info_map)
        dir_path_check = Path(dir_path)
        if dir_path_check.is_dir():
            txt_files = []
            all_files = os.listdir(dir_path)
            for filename in all_files:
                if filename.endswith(".txt"):
                    txt_files.append(filename)
            self.add_log("search_path_for_filenames_success", f"Successfully searched in {dir_path}"
                         f" and found {len(txt_files)} text files.", info_map)
            return txt_files
        else:
            raise NotADirectoryError("The specified path must be a directory")

    def _load_txt_file_to_list(self, path: str) -> List[str]:
        """ Reads a text file into a list.

        Parameters
        ----------
        path : str
            Path of the input file to be read.

        Returns
        -------
        List[str]
            A list of strings from a text file where each line of the file becomes a list element.

        Raises
        -------
        Exception
            If an error occurs while opening or reading the file.

        """
        info_map = {"class": self.__class__.__name__,
                    "function": self._load_txt_file_to_list.__name__,
                    }
        self.add_log("open_text_file", f"Attempting to open {path}.", info_map)
        try:
            with open(path) as text_file:
                list_of_elements = text_file.read().splitlines()
                load_message = f"Successfully opened {path} and read {len(list_of_elements)} lines."
                self.add_log("filter_pattern_file_load_log", load_message, info_map)
                return list_of_elements
        except Exception as e:
            raise e

    def _filter_variables_pool(self, filter_patterns: List[str], input_file_name: Optional[str]
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
        info_map = {"class": self.__class__.__name__,
                    "function": self._filter_variables_pool.__name__,
                    }
        exclude_keyword_location = 0
        exclude_keyword = "exclude"
        filter_by_exclusion = filter_patterns and filter_patterns[exclude_keyword_location] == exclude_keyword
        if filter_by_exclusion:
            filter_vars_msg = f"{input_file_name} has exclude-keyword '{exclude_keyword}' at"\
                f" position {exclude_keyword_location}. Performing filtering by exclusion."
            filter_pattern_matches = {key: self.variables_pool[key] for key in self.variables_pool.keys() if not
                                      any(re.match(pattern, key) for pattern in filter_patterns)}
        else:
            filter_vars_msg = f"{input_file_name} does NOT contain exclude-keyword '{exclude_keyword}'"\
                f" at position {exclude_keyword_location}. Performing filtering by inclusion."
            filter_pattern_matches = {key: self.variables_pool[key] for key in self.variables_pool.keys() if
                                      any(re.match(pattern, key) for pattern in filter_patterns)}
        self.add_log("filtering_log", filter_vars_msg, info_map)
        filter_log_count_msg = f"There were {len(filter_pattern_matches)} matches for the {len(filter_patterns)}"\
            f" filter patterns in the {input_file_name} file."
        self.add_log("num_filter_pattern_matches", filter_log_count_msg, info_map)
        return filter_pattern_matches

    def save_variables(self, save_path: str, dir_path: str,
                       exclude_info_maps: bool = False) -> None:
        """
        Reads a text file containing a list of keys and filters the variables pool by those keys.
        Saves resulting data pool to a json file in the given path to a directory.

        Parameters
        ----------
        save_path : str
            Path to the directory where the file will be saved.

        dir_path : str
            Path of the directory containing the files containing the keys for filtering.

        exclude_info_maps : bool
            Flag for whether or not the user wants to include info_maps data in their results files.

        """
        info_map = {"class": self.__class__.__name__,
                    "function": self.save_variables.__name__,
                    }
        self.add_log("exclude_info_maps", f"exclude_info_maps flag set to {exclude_info_maps}", info_map)
        list_of_filter_files = self._list_txt_file_names_in_dir(dir_path)
        for filter_file in list_of_filter_files:
            input_path = os.path.join(dir_path, filter_file)
            filter_patterns = self._load_txt_file_to_list(input_path)
            filtered_pool = self._filter_variables_pool(filter_patterns, filter_file)
            if exclude_info_maps:
                filtered_pool = self._exclude_info_maps(filtered_pool)
            file_path = os.path.join(save_path, self._generate_file_name(f"saved_variables_{filter_file}", "json"))
            self._dict_to_file_json(filtered_pool, file_path)

    def dump_variables(self, path: str, exclude_info_maps: bool = False) -> None:
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

        file_path = os.path.join(path, self._generate_file_name("all_variables", "json"))
        self._dict_to_file_json(pool, file_path)

    def dump_logs(self, path: str) -> None:
        """
        Dumps logs_pool into a json file in the given path to a directory.
        """
        file_path = os.path.join(path, self._generate_file_name("logs", "json"))
        self._dict_to_file_json(self.logs_pool, file_path)

    def dump_warnings(self, path: str) -> None:
        """
        Dumps warnings_pool into a json file in the given path to a directory.
        """
        file_path = os.path.join(path, self._generate_file_name("warnings", "json"))
        self._dict_to_file_json(self.warnings_pool, file_path)

    def dump_errors(self, path: str) -> None:
        """
        Dumps errors_pool into a json file in the given path to a directory.
        """
        file_path = os.path.join(path, self._generate_file_name("errors", "json"))
        self._dict_to_file_json(self.errors_pool, file_path)

    def dump_variable_names_and_contexts(
        self, path: str, exclude_info_maps: bool, format_option: str = "verbose"
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

        format_option : {"block", "inline", "verbose"}
            The selection for the formatting option of the text written to the variables names text file.

        Examples
        --------
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

        var_list = [f"_{exclude_info_maps=}, expect info_maps accordingly.\n"]
        for name, variable_data in self.variables_pool.items():
            if not variable_data["values"]:
                var_list.append(f"{name}: **NO VARIABLES**\n")
                continue

            parsable_dicts = []

            if not exclude_info_maps:
                parsable_dicts.append("info_maps")

            is_variable_nested = isinstance(variable_data["values"][0], Dict)
            if is_variable_nested:
                parsable_dicts.append("values")
            else:
                var_list.append(f"{name}\n")

            if format_option == "block":
                var_list.append(f"{name}\n")

            prefix = name
            if format_option == "block":
                prefix = " " * len(name)

            for parsable_dict in parsable_dicts:
                keys = variable_data[parsable_dict][0].keys()
                if format_option == "inline":
                    var_list.append(f"{name}.{parsable_dict}: {list(keys)}\n")
                else:
                    for key in keys:
                        var_list.append(f"{prefix}.{parsable_dict}: {key}\n")

        file_path = os.path.join(
            path, self._generate_file_name("variable_names", "txt")
        )
        self._list_to_file_txt(var_list, file_path)

    def dump_all_pools(self, path: str, exclude_info_maps: bool = False) -> None:
        """
        dumps all pool into the given path to a directory.
        """
        self.dump_variables(path, exclude_info_maps)
        self.dump_variable_names_and_contexts(path, exclude_info_maps)
        self.dump_errors(path)
        self.dump_logs(path)
        self.dump_warnings(path)

    def flush_pools(self) -> None:
        """
        Sets each pool to an empty dictionary.
        """
        self.variables_pool: Dict[str, OutputManager.pool_element_type] = {}
        self.warnings_pool: Dict[str, OutputManager.pool_element_type] = {}
        self.errors_pool: Dict[str, OutputManager.pool_element_type] = {}
        self.logs_pool: Dict[str, OutputManager.pool_element_type] = {}

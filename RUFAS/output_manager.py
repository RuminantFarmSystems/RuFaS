# !/usr/bin/env python3

from typing import Any, Dict, List, Union
import json
import os
import time

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
        key = self._generate_key(name, info_map)
        self._add_to_pool(self.errors_pool, key, msg, info_map)

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
        try:
            with open(path, "w") as json_file:
                json.dump(
                    Utility.make_serializable(data_dict, max_depth=3),
                    json_file,
                    indent=0,
                )
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
        try:
            with open(path, "w") as var_names_file:
                var_names_file.writelines(data_list)
        except Exception as e:
            raise e

    def _generate_file_name(self, base_name: str, extension: str = "json") -> str:
        """
        Returns a file name using the given base_name and timestamp.
        """
        timestamp = time.strftime(r"%d-%b-%Y_%a_%H-%M-%S", time.localtime())
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

    def _load_input_txt_file_names_to_list(self, dir_path: str) -> List[str]:
        """ Looks in inputs directory for txt file names.

        Parameters
        ----------
        path : str
            Path of the input directory to be searched.

        Returns
        -------
        List
            A list of input txt file names.

        """

        txt_files = []
        for filename in os.listdir(dir_path):
            if filename.endswith(".txt"):
                txt_files.append(filename)
        return txt_files

    def _load_txt_file_to_list(self, path: str) -> List[str]:
        """ Reads a text file into a list.

        Parameters
        ----------
        path : str
            Path of the input file to be read.

        Returns
        -------
        List
            A list of keys the user has selected to filter the variables pool.

        Raises
        -------
        Exception
            If an error occurs while opening or reading the file.

        """
        try:
            with open(path) as keys_doc:
                return keys_doc.read().splitlines()
        except Exception as e:
            raise e

    def _filter_variables_pool(self, inclusion_keys: List[str]):
        """
        Takes the list of keys the user wants in their final data pool,
        filters the variables pool accordingly, and returns the filtered pool.

        Parameters
        ----------
        inclusion_keys : List[str]
            A list of keys the user has selected to filter the variables pool.

        Returns
        -------
        Dict[str, OutputManager.pool_element_type]
            The variables_pool with only the values paired with the keys
            from the inclusion_keys list remaining.

        """
        return {key: self.variables_pool[key] for key in inclusion_keys if key in self.variables_pool.keys()}

    def save_variables(self, path: str, dir_path: str,
                       exclude_info_maps: bool = False) -> None:
        """
        Reads a text file containing a list of keys and filters the variables pool by those keys.
        Saves resulting data pool to a json file in the given path to a directory.

        Parameters
        ----------
        path : str
            Path to the directory where the file will be saved.

        dir_path : str
            Path of the input file containing the list of keys for inclusion filter.

        exclude_info_maps : bool
            Flag for whether or not the user wants to inlcude info_maps data in their results files.

        """
        list_of_input_files = self._load_input_txt_file_names_to_list(dir_path)
        for input_file in list_of_input_files:
            input_path = dir_path + input_file
            inclusion_keys = self._load_txt_file_to_list(input_path)
            filtered_pool = self._filter_variables_pool(inclusion_keys)
            final_pool = filtered_pool
            if exclude_info_maps:
                final_pool = self._exclude_info_maps(filtered_pool)
            file_path = os.path.join(path, self._generate_file_name(f"saved_variables_{input_file}", "json"))
            self._dict_to_file_json(final_pool, file_path)

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

        Parameters
        ----------
        path : str
            Path to the directory where the file will be saved.

        """
        file_path = os.path.join(path, self._generate_file_name("logs", "json"))
        self._dict_to_file_json(self.logs_pool, file_path)

    def dump_warnings(self, path: str) -> None:
        """
        Dumps warnings_pool into a json file in the given path to a directory.

        Parameters
        ----------
        path : str
            Path to the directory where the file will be saved.

        """
        file_path = os.path.join(path, self._generate_file_name("warnings", "json"))
        self._dict_to_file_json(self.warnings_pool, file_path)

    def dump_errors(self, path: str) -> None:
        """
        Dumps errors_pool into a json file in the given path to a directory.

        Parameters
        ----------
        path : str
            Path to the directory where the file will be saved.

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
        Dumps all pool into the given path to a directory.

        Parameters
        ----------
        path : str
            Path to the directory where the file will be saved.

        exclude_info_maps : bool
            Flag for whether or not the user wants to inlcude info_maps data in their results files.

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

# !/usr/bin/env python3

from typing import Any, Dict, List, Union
import os
import time


class OutputManager (object):
    """
    Output manager for RuFaS simulation results. Works by collecting variables,
    logs, warnings, and errors into separate pools, and populates requested
    output channels from the pools once the simulation is done. 

    OutputManager is singleton, i.e., only one instance of it can exist. After
    the first instance is created, future calls to the constructor method 
    returns the first instance. Also, the initializer method only works once.

    Attributes
    ----------
    variables_pool : Dict[str, Dict[str, List[Dict[str, Any]] | List[Any]]]
        Contains variables reported to the output manager
    warnings_pool : Dict[str, Dict[str, List[Dict[str, Any]] | List[Any]]]
        Contains warnings reported to the output manager
    errors_pool : Dict[str, Dict[str, List[Dict[str, Any]] | List[Any]]]
        Contains errors reported to the output manager
    logs_pool : Dict[str, Dict[str, List[Dict[str, Any]] | List[Any]]]
        Contains logs reported to the output manager 
    """
    __instance = None
    pool_element_type = Dict[str, List[Dict[str, Any]] | List[Any]]

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(OutputManager, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        if OutputManager.__instance is None:
            OutputManager.__instance = self
            self.variables_pool: Dict[str,
                                      OutputManager.pool_element_type] = {}
            self.warnings_pool: Dict[str, OutputManager.pool_element_type] = {}
            self.errors_pool: Dict[str, OutputManager.pool_element_type] = {}
            self.logs_pool: Dict[str, OutputManager.pool_element_type] = {}
            self.add_log("init_log", "Output Manager instantiated.",
                         info_map={"class": self.__class__.__name__,
                                   "function": self.__init__.__name__})            

    def _pool_element_factory(self) -> pool_element_type:
        """Factory for elements added to pools"""
        info_maps: List[Dict[str, Any]] = []
        values: List[Any] = []
        return {'info_maps': info_maps, 'values': values}

    def _add_to_pool(self, pool: Dict[str, pool_element_type],
                     key: str, value: Any, info_map: Dict[str, Any]) -> None:
        """Adds value and info map at key in the given pool."""
        key_not_exists_in_pool = pool.get(key) is None
        if key_not_exists_in_pool:
            pool[key] = self._pool_element_factory()
        pool[key]['info_maps'].append(info_map)
        pool[key]['values'].append(value)

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
        info_map["suffix"] : str, optional
            If present, gets appended to the key
        info_map["suppress_prefix"] : bool, optional
            If present and True, suppresses the automated prefix generation.
            Has no effect on manual prefix overrides.        
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
        """
        key = self._generate_key(name, info_map)
        self._add_to_pool(self.errors_pool, key, msg, info_map)

    def _generate_key(self, name: str,
                      info_map: Dict[str, Union[str, bool]]) -> str:
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
            raise KeyError("'class' were not found in info_map")
        if info_map.get("function") is None:
            raise KeyError("'function' were not found in info_map")

        prefix = ""
        if info_map.get("prefix") is not None:
            prefix = info_map.get("prefix") + "."
        elif not info_map.get("suppress_prefix", False):
            prefix = self._get_prefix(info_map.get(
                "class"), info_map.get("function")) + "."

        suffix = ""
        if info_map.get("suffix") is not None:
            suffix = "." + info_map.get("suffix")
        elif not info_map.get("suppress_suffix", False):
            suffix = f".{self.counter}"
            self.counter += 1

        return f"{prefix}{name}{suffix}"

    def _get_prefix(self, caller_class: str, caller_function: str) -> str:
        """
        Returns the prefix for a key in the pool.

        Parameters
        ----------
        caller_class : str
            The name of the class in which this key-value pair is originated
        function : str
            The name of the function in which this key-value pair is originated

        Returns
        -------
        str
            {caller_class}.{caller_function}
        """
        return f"{caller_class}.{caller_function}"

    def _get_time_based_suffix(self) -> str:
        """
        Returns a suffix for a key in the pool by using timestamp in ns.
        This guarantees that no name collision will happen.
        """
        return str(time.time_ns())

    def _dict_to_file_json(self, dict: Dict[str, Any], path: str) -> None:
        """Saves a dictionary into a JSON file"""
        try:
            with open(path, 'w') as json_file:
                json_file.write(str(dict))
        except Exception as e:
            raise e

    def _generate_file_name(self, base_name: str, extension: str = "json") -> str:
        """
        Returns a file name using the given base_name and timestamp.
        """
        return f"{base_name}_{self._get_time_based_suffix()}.{extension}"

    def save_variables(self, path: str) -> None:
        """
        Saves the variables_pool into a json file in the given path to a directory.
        """
        file_path = os.path.join(
            path, self._generate_file_name("variables", "json"))
        self._dict_to_file_json(self.variables_pool, file_path)

    def save_logs(self, path: str) -> None:
        """
        Saves the logs_pool into a json file in the given path to a directory.
        """
        file_path = os.path.join(
            path, self._generate_file_name("logs", "json"))
        self._dict_to_file_json(self.logs_pool, file_path)

    def save_warnings(self, path: str) -> None:
        """
        Saves the warnings_pool into a json file in the given path to a directory.
        """
        file_path = os.path.join(
            path, self._generate_file_name("warnings", "json"))
        self._dict_to_file_json(self.warnings_pool, file_path)

    def save_errors(self, path: str) -> None:
        """
        Saves the errors_pool into a json file in the given path to a directory.
        """
        file_path = os.path.join(
            path, self._generate_file_name("errors", "json"))
        self._dict_to_file_json(self.errors_pool, file_path)

    def save_all_pools(self, path: str) -> None:
        """
        Saves all pool into the given path to a directory.
        """
        self.save_variables(path)
        self.save_errors(path)
        self.save_logs(path)
        self.save_warnings(path)

    def flush_pools(self) -> None:
        """
        Sets all pools to an empty dictionary.
        """
        self.variables_pool: Dict[str, Any] = {}
        self.warnings_pool: Dict[str, Any] = {}
        self.errors_pool: Dict[str, Any] = {}
        self.logs_pool: Dict[str, Any] = {}

# !/usr/bin/env python3

from typing import Any, Dict, List, Union
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
    variables_pool : Dict[str, Any]
        Contains variables reported to the output manager
    warnings_pool : Dict[str, Any]
        Contains warnings reported to the output manager
    errors_pool : Dict[str, Any]
        Contains errors reported to the output manager
    logs_pool : Dict[str, Any]
        Contains logs reported to the output manager 
    """
    __instance = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(OutputManager, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        if OutputManager.__instance is None:
            OutputManager.__instance = self
            self.variables_pool: Dict[str, Any] = {}
            self.warnings_pool: Dict[str, Any] = {}
            self.errors_pool: Dict[str, Any] = {}
            self.logs_pool: Dict[str, Any] = {}
            self.add_log("init_log", "Output Manager instantiated.",
                         info_map={'caller_class': self.__class__.__name__,
                                   'caller_function': self.__init__.__name__})

    def add_variable(self, name: str, value: Any,
                     info_map: Dict[str, Union[str, bool]]) -> None:
        """
        Adds a variable to the pool.

        Parameters
        ----------
        name : str
            The name of the variable
        value : Any
            The value of the variable
        info_map : Dict[str, Union[str,bool]]
            Additional args, some are non-optional
        info_map['caller_class'] : str
            The name of the class which called this function
        info_map['caller_function'] : str
            The name of the function which called this function 
        info_map['prefix'] : str, optional
            If present, overrides the automated prefix
        info_map['suffix'] : str, optional
            If present, overrides the automated suffix
        info_map['suppress_prefix'] : bool, optional
            If present and True, suppresses the automated prefix generation.
            Has no effect on manual prefix overrides.
        info_map['suppress_suffix'] : bool, optional
            If present and True, suppresses the automated suffix generation.
            Has no effect on manual suffix overrides.
        info_map['enforce_override'] : bool, optional
            If present and True, overrides the existing value in the pool if a
            key collision happens.
        info_map['fail_silently'] : bool, optional
            If present and True, suppresses raising error if a key collision
            happens.

        Raises
        ------
        ValueError
            If a key collision happens in the pool and either
            info_map['fail_silently'] or info_map['enforce_override'] 
            are not set to True.
        """
        key = self._generate_key(name, info_map)
        key_not_exists = self.variables_pool.get(key) is None
        if key_not_exists:
            self.variables_pool[key] = value
            return
        info_map['key'] = key
        info_map['caller_function'] = self.add_variable.__name__
        info_map['caller_class'] = self.__class__.__name__
        if info_map.get('enforce_override', False):
            self.variables_pool[key] = value
            self.add_warning('key_collision',
                             "Key collision happened; the value was overriden per given flag.",
                             info_map)
            return
        if info_map.get('fail_silently', False):
            self.add_error('key_collision',
                           "Key collision happened; the event was ignored per given flag.",
                           info_map)
            return
        raise ValueError(f"Key {key} already exists in the variables_pool."
                         + "Consider using different name, prefix/suffix;"
                         + "or turn the automated prefix/suffix generation on."
                         + f"info_map is: {info_map}"
                         )

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
        info_map['caller_class'] : str
            The name of the class which called this function
        info_map['caller_function'] : str
            The name of the function which called this function 
        """
        key = self._generate_key(name,
                                 {
                                     'caller_class': info_map['caller_class'],
                                     'caller_function': info_map['caller_function']})
        self.logs_pool[key] = {'msg': msg, 'info_map': info_map}

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
        info_map['caller_class'] : str
            The name of the class which called this function
        info_map['caller_function'] : str
            The name of the function which called this function 
        """
        key = self._generate_key(name,
                                 {
                                     'caller_class': info_map['caller_class'],
                                     'caller_function': info_map['caller_function']})
        self.warnings_pool[key] = {'msg': msg, 'info_map': info_map}

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
        info_map['caller_class'] : str
            The name of the class which called this function
        info_map['caller_function'] : str
            The name of the function which called this function 
        """
        key = self._generate_key(name,
                                 {
                                     'caller_class': info_map['caller_class'],
                                     'caller_function': info_map['caller_function']})
        self.errors_pool[key] = {'msg': msg, 'info_map': info_map}

    def _generate_key(self, name: str,
                      info_map: Dict[str, Union[str, bool]]) -> str:
        """
        Generates key for the pool.
        See 'add_variable' docs for detailed arg description.

        Raises
        ------
        KeyError
            If either info_map['caller_class'] or info_map['caller_function'] are 
            not present.
        """
        if info_map.get('caller_class') is None:
            raise KeyError("'caller_class' were not found in info_map")
        if info_map.get('caller_function') is None:
            raise KeyError("'caller_function' were not found in info_map")

        prefix = ""
        if info_map.get('prefix') is not None:
            prefix = info_map.get('prefix') + "."
        elif not info_map.get('suppress_prefix', False):
            prefix = self._get_prefix(info_map.get(
                'caller_class'), info_map.get('caller_function')) + "."

        suffix = ""
        if info_map.get('suffix') is not None:
            suffix = "." + info_map.get('suffix')
        elif not info_map.get('suppress_suffix', False):
            suffix = "." + self._get_time_based_suffix()

        return f"{prefix}{name}{suffix}"

    def _get_prefix(self, caller_class: str, caller_function: str) -> str:
        """
        Returns the prefix for a key in the pool.

        Parameters
        ----------
        caller_class : str
            The name of the class in which this key-value pair is originated
        caller_function : str
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
        return str(time.time())

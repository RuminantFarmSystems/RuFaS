# !/usr/bin/env python3

from typing import Any, Dict, List, Union
import time


class OutputManager (object):
    """
    Output manager for RufaS simulation results. Works by collecting variables
    into the pool, and populates requested output channels from the pool once
    the simulation is done. Warnings and errors are added to their own pools.

    Attributes
    ----------
    pool : Dict[str, Any]
        Contains variables reported from simulation engine
    warnings_pool : Dict[str, Any]
        Contains warnings reported from simulation engine
    errors_pool : Dict[str, Any]
        Contains errors reported from simulation engine
    logs_pool : Dict[str, Any]
        Contains logs reported from simulation engine
    """

    def __init__(self) -> None:
        self.pool: Dict[str, Any] = {}
        self.warnings_pool: Dict[str, Any] = {}
        self.errors_pool: Dict[str, Any] = {}
        self.logs_pool: Dict[str, Any] = {}
        self.add_log("Output Manager instantiated.",
                     caller_class=self.__class__.__name__,
                     caller_function=self.__init__.__name__)

    def add_variable(self, name: str, value: Any,
                    **kwargs: Dict[str, Union[str, bool]]) -> None:
        """
        Adds a variable to the pool.

        Parameters
        ----------
        name : str
            The name of the variable
        value : Any
            The value of the variable
        kwargs : Dict[str, Union[str,bool]]
            Additional args, some are non-optional
        kwargs['caller_class'] : str
            The name of the class which called this function
        kwargs['caller_function'] : str
            The name of the function which called this function 
        kwargs['prefix'] : str, optional
            If present, overrides the automated prefix
        kwargs['suffix'] : str, optional
            If present, overrides the automated suffix
        kwargs['suppress_prefix'] : bool, optional
            If present and True, suppresses the automated prefix generation.
            Has no effect on manual prefix overrides.
        kwargs['suppress_suffix'] : bool, optional
            If present and True, suppresses the automated suffix generation.
            Has no effect on manual suffix overrides.
        kwargs['enforce_override'] : bool, optional
            If present and True, overrides the existing value in the pool if a
            key collision happens.
        kwargs['fail_silently'] : bool, optional
            If present and True, suppresses raising error if a key collision
            happens.

        Raises
        ------
        ValueError
            If a key collision happens in the pool and either
            **kwargs['fail_silently'] or **kwargs['enforce_override'] 
            are not set to True.
        """
        function_name = self.add_to_pool.__name__
        key = self.__generate_key(name, kwargs)
        key_not_exists = self.pool.get(key) is None
        if key_not_exists:
            self.pool[key] = value
            return
        if kwargs.get('enforce_override', False):
            self.pool[key] = value
            self.add_warning(
                "Key collision happened; the value was overriden per given flag.",
                self.__class__.__name__, function_name, [key], kwargs)
            return
        if kwargs.get('fail_silently', False):
            self.add_warning(
                "Key collision happened; the event was ignored per given flag.",
                self.__class__.__name__, function_name, [key], kwargs)
            return
        raise ValueError(f"Key {key} already exists in the pool." +
                         "Consider using different name, prefix/suffix;" +
                         "or turn the automated prefix/suffix generation on"
                         )

    def add_log(
            self, msg: str, *args: List[Any], **kwargs: Dict[Any, Any]) -> None:
        """
        Adds a log message to the pool of logs.

        Parameters
        ----------
        msg : str
            The log message to be added to the pool
        *args: List[Any]
            Contains any additional information to be added to the message  
        **kwargs: Dict[Any, Any]
            Additional args, some are non-optional
        kwargs['caller_class'] : str
            The name of the class which called this function
        kwargs['caller_function'] : str
            The name of the function which called this function 
        """
        key = self.__generate_key('log_entry', kwargs)
        self.logs_pool[key] = {'msg': msg, 'args': args, 'kwargs': kwargs}

    def add_warning(
            self, msg: str, *args: List[Any], **kwargs: Dict[Any, Any]) -> None:
        """
        Adds a warning message to the pool of warnings.

        Parameters
        ----------
        msg : str
            The warning message to be added to the pool
        *args: List[Any]
            Contains any additional information to be added to the message  
        **kwargs: Dict[Any, Any]
            Additional args, some are non-optional
        kwargs['caller_class'] : str
            The name of the class which called this function
        kwargs['caller_function'] : str
            The name of the function which called this function 
        """
        key = self.__generate_key('warning_entry', kwargs)
        self.warnings_pool[key] = {'msg': msg, 'args': args, 'kwargs': kwargs}

    def add_error(self, msg: str, caller_class: str, caller_function: str,
                  *args: List[Any], **kwargs: Dict[Any, Any]) -> None:
        """
        Adds an error message to the pool of errors.

        Parameters
        ----------
        msg : str
            The error message to be added to the pool
        *args: List[Any]
            Contains any additional information to be added to the message  
        **kwargs: Dict[Any, Any]
            Additional args, some are non-optional
        kwargs['caller_class'] : str
            The name of the class which called this function
        kwargs['caller_function'] : str
            The name of the function which called this function 
        """
        key = self.__generate_key('error_entry', kwargs)
        self.errors_pool[key] = {'msg': msg, 'args': args, 'kwargs': kwargs}

    def __generate_key(self, name: str,
                       **kwargs: Dict[str, Union[str, bool]]) -> str:
        """
        Generates key for the pool.
        See 'add_to_pool' docs for detailed arg description.

        Raises
        ------
        KeyError
            If either kwargs['caller_class'] or kwargs['caller_function'] are 
            not present.
        """
        if kwargs.get('caller_class') is None:
            raise KeyError("'caller_class' were not found in kwargs")
        if kwargs.get('caller_function') is None:
            raise KeyError("'caller_function' were not found in kwargs")

        prefix = ""
        if kwargs.get('prefix') is not None:
            prefix = kwargs.get('prefix') + "."
        elif not kwargs.get('suppress_prefix', False):
            prefix = self.__get_prefix(kwargs.get(
                'caller_class'), kwargs.get('caller_function')) + "."

        suffix = ""
        if kwargs.get('suffix') is not None:
            suffix = "." + kwargs.get('suffix')
        elif not kwargs.get('suppress_suffix', False):
            suffix = "." + self.__get_suffix()

        return f"{prefix}{name}{suffix}"

    def __get_prefix(self, caller_class: str, caller_function: str) -> str:
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

    def __get_suffix(self) -> str:
        """
        Returns a suffix for a key in the pool by using timestamp in ns.
        This gurrantees that no name collision will happen.
        """
        return str(time.time())

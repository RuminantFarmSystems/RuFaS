# !/usr/bin/env python3

from typing import Any, Dict, Optional
import time

class OutputManager (object):
    """
    Output manager for Rufas simulation results. Works by collecting variables into
    the pool, and populates requested output channels from the pool once the simulation
    is done. 

    Attributes
    ----------
        pool (Dict[str, Any]): Contains variables reported from simulation engine
    """

    def __init__(self) -> None:
        self.pool: Dict[str, Any] = {}

    def add_to_pool(self, name: str, value: Any, **kwargs: Dict[Any, Any]) -> None:
        """
        Adds a variable to the output pool.

        Parameters
        ----------
        name : str
            The name of the variable
        value : Any
            The value of the variable
        kwargs : Dict[Any, Any]
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
            Has no effect on manual prefixes.
        kwargs['suppress_suffix'] : bool, optional
            If present and True, suppresses the automated suffix generation.
            Has no effect on manual suffix.
        kwargs['enforce_override'] : bool, optional
            If present and True, overrides the existing value in the pool if a
            name collision happens.
        kwargs['fail_silently'] : bool, optional
            If present and True, suppresses raising error if a name collision
            happens.

        Raises
        ------
        ValueError
            If a name collision happens in the pool and either
            **kwargs['fail_silently'] or **kwargs['enforce_override'] 
            are not set to True.
        """
        key = self.__generate_key(name, kwargs)
        key_not_exists = self.pool.get(key) is None
        if key_not_exists:
            self.pool[key] = value
            return
        if kwargs.get('enforce_override', False):
            self.pool[key] = value
            return
        if not kwargs.get('fail_silently', False):
            raise ValueError(f"Key {key} already exists in the pool." +
                             "Consider using different name, prefix/suffix;" +
                             "or turn the automated prefix/suffix generation on"
                             )

    def __generate_key(self, name: str, **kwargs: Dict[Any, Any]) -> str:
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
        Returns a suffix for a key in the pool by usin timestamp in ns.
        This gurrantees that no name collision will happen.
        """
        return str(time.time())

    def __read_json_configs(self) -> None:
        pass

    def save_to_file(self) -> None:
        pass

# !/usr/bin/env python3

import json
import re

import pandas as pd
from RUFAS.output_manager import OutputManager
from typing import Any, Dict


om = OutputManager()


class InputManager:
    """
    Input Manager class responsible for loading, validating, and providing access to input data.
    """
    __instance = None

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(InputManager, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        if InputManager.__instance is None:
            InputManager.__instance = self
        self.__metadata: Dict[str, Any] = {}
        self.__pool: Dict[str, Any] = {}

    def _load_metadata(self, metadata_path: str = "input/example_metadata.json") -> None:
        """
        Loads metadata from json file to IM metadata dict.

        Parameters
        ----------
        metadata_path : str
            The path to the metadata file.

        Raises
        ------
        Exception
            If an error occurs while opening or reading the metadata_path file.

        """
        info_map = {"class": self.__class__.__name__,
                    "function": self._load_metadata.__name__,
                    }
        om.add_log("load_metadata_attempt", f"Attempting to load metadata from {metadata_path}.", info_map)
        try:
            with open(metadata_path) as metadata_file:
                self.__metadata = json.load(metadata_file)
                om.add_log("load_metadata_success", f"Successfully loaded metadata from {metadata_path}", info_map)
        except Exception as e:
            raise e

    def _load_data(self) -> None:
        """
        Loads data from JSON or CSV file.

        Raises
        ------
        Exception
            If an error occurs while opening or reading a data file.
        """

        files_details = self.__metadata["files"]
        path_key = "path"
        info_map = {"class": self.__class__.__name__,
                    "function": self._load_data.__name__,
                    }
        for key, details in files_details.items():
            file_path = details[path_key]
            om.add_log("load_data_attempt", f"Attempting to load data for {key} from {file_path}.", info_map)
            try:
                if details["type"] == "json":
                    with open(file_path) as json_file:
                        data = json.load(json_file)
                        self.__pool[key] = data
                        om.add_log("load_data_successful", f"Successfully loaded data for {key} from {file_path}.",
                                   info_map)
                elif details["type"] == "csv":
                    with open(file_path, "r") as csv_file:
                        data_frame = pd.read_csv(csv_file)
                        data_dict = {column: data_frame[column].tolist() for column in data_frame.columns}
                        self.__pool[key] = data_dict
                        om.add_log("load_data_successful", f"Successfully loaded data for {key} from {file_path}.",
                                   info_map)
                else:
                    om.add_warning("InputManager load data file is not csv/json",
                                   f"{key} data must be available in either csv or json file type.",
                                   info_map)
            except Exception as e:
                raise e

    def _validate_data(self, eager_termination: bool = True) -> bool:
        """
        Validates input data and attempts to fix any invalid input data.

        Parameters
        ----------
        eager_termination : bool, default=True
            If true, the process will be terminated upon finding invalid data.

        Returns
        -------
        bool
            True if all data is valid; False otherwise.
        """
        info_map = {"class": self.__class__.__name__,
                    "function": self._validate_data.__name__,
                    }
        valid_elements_counter = 0
        invalid_elements_counter = 0
        fixed_elements_counter = 0
        invalid_critical_elements_counter = 0
        total_elements_checked_counter = 0

        for key in self.__pool.keys():
            for variable, value in self.__pool[key].items():
                total_elements_checked_counter += 1
                if self._validate_element(key, variable, value):
                    valid_elements_counter += 1
                else:
                    invalid_elements_counter += 1
                    is_data_fixed = self._fix_data(variable, value)
                    if is_data_fixed:
                        fixed_elements_counter += 1
                    elif not is_data_fixed and eager_termination:
                        invalid_critical_elements_counter += 1
                        return False
                    else:
                        invalid_critical_elements_counter += 1

        om.add_log("Total Valid Elements", f"{valid_elements_counter=}", info_map)
        om.add_log("Total Invalid Elements", f"{invalid_elements_counter=}", info_map)
        om.add_log("Total Fixed Elements", f"{fixed_elements_counter=}", info_map)
        om.add_log("Total Checked Elements", f"{total_elements_checked_counter=}", info_map)
        om.add_log("Total Invalid Critical Elements", f"{invalid_critical_elements_counter=}", info_map)

        if invalid_critical_elements_counter > 0:
            return False

        return True

    def _validate_element(self, module_key: str, variable_name: str, value: Any) -> bool:
        """
        Performs data validation checks on data elements.

        Parameters
        ----------
        module_key : str
            The key of the module to which the data to validate belongs.

        variable_name : str
            The name of the variable to validate.

        value : Any
            The value of the data to validate.


        Returns
        -------
        bool
            True if the data is valid, False otherwise.
        """
        info_map = {"class": self.__class__.__name__,
                    "function": self._validate_element.__name__,
                    }
        property_map_key = self.__metadata["files"][module_key]["properties"]
        if isinstance(value, dict):
            for nested_key, nested_value in value.items():
                self._validate_element(module_key, nested_key, nested_value)
        elif variable_name not in self.__metadata["properties"][property_map_key].values():
            om.add_error(f"Variable not found in {module_key} metadata properties.", f"{variable_name=}", info_map)
            return False
        else:
            variable_properties = self.__metadata["properties"][property_map_key][variable_name]
            var_type = variable_properties["type"]
            if var_type == "string":
                if variable_properties["pattern"]:
                    is_match = bool(re.match(variable_properties["pattern"], value))
                    if not is_match:
                        om.add_warning(f"String variable must match pattern {variable_properties['pattern']}.",
                                       f"{variable_name=}",
                                       info_map)
                    return is_match
                else:
                    om.add_error("Metadata must have pattern to match string to.", f"{variable_name=}", info_map)
                    return False
            elif var_type == "number":
                if variable_properties["minimum"] and variable_properties["maximum"]:
                    is_in_range = variable_properties["minimum"] <= value <= variable_properties["maximum"]
                    if not is_in_range:
                        om.add_warning("Value out of range.", f"{variable_name=}", info_map)
                    return is_in_range
                elif variable_properties["minimum"]:
                    is_in_range = variable_properties["minimum"] <= value
                    if not is_in_range:
                        om.add_warning("Value out of range.", f"{variable_name=}", info_map)
                    return is_in_range
                elif variable_properties["maximum"]:
                    is_in_range = value <= variable_properties["maximum"]
                    if not is_in_range:
                        om.add_warning("Value out of range.", f"{variable_name=}", info_map)
                    return is_in_range
                else:
                    return True
            elif var_type == "array":
                if variable_properties["minimum_length"] and variable_properties["maximum_length"]:
                    is_in_range = variable_properties["minimum_length"] <= value <= \
                        variable_properties["maximum_length"]
                    if not is_in_range:
                        om.add_warning("Array out of length range.", f"{variable_name=}", info_map)
                    return is_in_range
                elif variable_properties["minimum_length"]:
                    is_in_range = variable_properties["minimum_length"] <= value
                    if not is_in_range:
                        om.add_warning("Array out of length range.", f"{variable_name=}", info_map)
                    return is_in_range
                elif variable_properties["maximum_length"]:
                    is_in_range = value <= variable_properties["maximum_length"]
                    if not is_in_range:
                        om.add_warning("Array out of length range.", f"{variable_name=}", info_map)
                    return is_in_range
                else:
                    return False
            elif var_type == "boolean":
                return value in (True, False)
            else:
                om.add_error("Metadata properties must be type string, number, array or boolean.",
                             f"{variable_name=}, provided type:{var_type}",
                             info_map)
                return False

    def _fix_data(self, key: str, value: Any) -> bool:
        """
        Attempt to fix the invalid data.

        Parameters
        ----------
        key : str
            The key of the data to fix.

        value : Any
            The value of the data to fix.

        Returns
        -------
        bool
            True if the data is fixed, False otherwise.
        """
        # Attempt to fix the invalid data
        # Return True if the data is fixed, False otherwise

        # TODO in fix_data fun branch
        # where element is fixed, place this warning:
        # om.add_warning("Data fixed", f"Invalid data fixed: {key=}; {value=}", info_map)
        # where data is not fixable:
        # om.add_error("Data not fixable.", f"Unable to fix the invalid data: {key=}, {value=}.", info_map)
        pass

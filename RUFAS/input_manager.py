# !/usr/bin/env python3

from functools import reduce
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

    def start_data_processing(self, metadata_path: str,
                              eager_termination: bool = True) -> bool:
        """
        Starts the pipeline for organizing metadata and input data processing.

        Parameters
        ----------
        metadata_path : str
            File path to the metadata.
        eager_termination : bool, default=True
            If True, the process will be terminated as soon as finding invalid data and failing to fix it.
            If False, the process will be terminated after going through and validating the entire data.

        Returns
        -------
        bool
            Flag indicating whether input data is valid.
        """
        self._load_metadata(metadata_path)
        self._load_data()
        is_input_data_valid = self._validate_data(eager_termination)
        return is_input_data_valid

    def _load_metadata(self, metadata_path: str) -> None:
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
        invalid_critical_elements_counter = 0
        total_elements_checked_counter = 0

        for module_key in self.__pool.keys():
            property_map_key = self.__metadata["files"][module_key]["properties"]
            module_properties = self.__metadata["properties"][property_map_key]
            for element in module_properties.keys():
                total_elements_checked_counter += 1
                is_valid_element = self._validate_element(module_key, element, property_map_key)
                if is_valid_element:
                    valid_elements_counter += 1
                elif not is_valid_element and eager_termination:
                    invalid_critical_elements_counter += 1
                    return False
                else:
                    invalid_critical_elements_counter += 1

        om.add_log("Total Valid Elements", f"{valid_elements_counter=}", info_map)
        om.add_log("Total Checked Elements", f"{total_elements_checked_counter=}", info_map)
        om.add_log("Total Invalid Critical Elements", f"{invalid_critical_elements_counter=}", info_map)

        if invalid_critical_elements_counter > 0:
            return False

        return True

    def _validate_element(self, module_key: str, element: str,
                          property_map_key: str, eager_termination: bool = True) -> bool:
        """
        Perform data validation checks.

        Parameters
        ----------
        module_key : str
            The module whose data is being validated.

        element : str
            The key of the data to validate.

        property_map_key : str
            The metadata properties section keyword for the data input file being checked.

        eager_termination : bool, default=True
            If true, the process will be terminated upon finding invalid data.

        Returns
        -------
        bool
            True if the data is valid, False otherwise.
        """
        info_map = {"class": self.__class__.__name__,
                    "function": self._validate_element.__name__,
                    }
        element_hierarchy = element.split(".")
        variable_to_check = reduce(lambda d, key: d[key], element_hierarchy,
                                   self.__metadata["properties"][property_map_key])
        var_type = variable_to_check["type"]
        is_nested = var_type == "object"
        if is_nested:
            children_status: Dict[str, bool] = {}
            false_counter = 0
            for nested_key in variable_to_check.keys():
                whole_key = f"{element}.{nested_key}"
                child_status = self._validate_element(self, whole_key, property_map_key, eager_termination)
                if eager_termination and not child_status:
                    return False
                children_status[whole_key] = child_status
                if not child_status:
                    om.add_warning("Invalid nested element found", f"{whole_key=}", info_map)
                    false_counter += 1
            is_valid = false_counter == 0
            if is_valid:
                return True
            else:
                invalid_child_vars = [key for key, value in children_status.items() if value is False]
                om.add_warning("Invalid nested element(s) found",
                               f"{invalid_child_vars=}",
                               info_map)
                return False
        else:
            var_name = element_hierarchy[-1]
            try:
                input_data_value = reduce(lambda d, key: d[key], element_hierarchy, self.__pool[module_key])
            except KeyError as e:
                raise KeyError(f"Key {var_name} not found in pool: {e}")

            type_validation_dict = {"string":
                                    self._validate_string_type_element(variable_to_check, var_name, input_data_value),
                                    "number":
                                    self._validate_num_type_element(variable_to_check, var_name, input_data_value),
                                    "array":
                                    self._validate_array_type_element(variable_to_check, var_name, input_data_value),
                                    "bool":
                                    True}
            is_valid = type_validation_dict.get(var_type)

            if is_valid:
                return True
            elif is_valid is None:
                raise Exception("Element must be type number, array, string, or bool")
            else:
                is_fixed = self._fix_data(module_key, element_hierarchy)
                return is_fixed

    def _validate_array_type_element(self, variable_to_check: Dict[str, Any], var_name: str,
                                     input_data_value: list) -> bool:
        """Validates a __pool element of type array."""
        info_map = {"class": self.__class__.__name__,
                    "function": self._validate_array_type_element.__name__,
                    }
        maximum_length = variable_to_check.get("maximum_length")
        minimum_length = variable_to_check.get("minimum_length")
        is_in_range = True
        if maximum_length is not None and minimum_length is not None:
            is_in_range = variable_to_check["minimum_length"] <= len(input_data_value) <= \
                variable_to_check["maximum_length"]
            warning_string = f"Array length not in range[{minimum_length}, {maximum_length}]"
        elif minimum_length is not None:
            is_in_range = variable_to_check["minimum_length"] <= len(input_data_value)
            warning_string = f"Array length less than {minimum_length}."
        elif maximum_length is not None:
            is_in_range = len(input_data_value) <= variable_to_check["maximum_length"]
            warning_string = f"Array length more than {maximum_length}."

        if not is_in_range:
            om.add_warning(warning_string, f"{var_name=}", info_map)

        return is_in_range

    def _validate_num_type_element(self, variable_to_check: Dict[str, Any], var_name: str,
                                   input_data_value: int) -> bool:
        """Validates a __pool number element."""
        info_map = {"class": self.__class__.__name__,
                    "function": self._validate_num_type_element.__name__,
                    }
        minimum_value = variable_to_check.get("minimum")
        maximum_value = variable_to_check.get("maximum")
        is_in_range = True
        if minimum_value is not None and maximum_value is not None:
            is_in_range = minimum_value <= input_data_value <= maximum_value
            warning_string = f"Value not in range [{minimum_value}, {maximum_value}]."
        elif minimum_value is not None:
            is_in_range = minimum_value <= input_data_value
            warning_string = f"Value less than {minimum_value}."
        elif maximum_value is not None:
            is_in_range = input_data_value <= maximum_value
            warning_string = f"Value greater than {maximum_value}."

        if not is_in_range:
            om.add_warning(warning_string, f"{var_name=}", info_map)

        return is_in_range

    def _validate_string_type_element(self, variable_to_check: Dict[str, Any], var_name: str,
                                      input_data_value: str) -> bool:
        """Validates a __pool string element."""
        info_map = {"class": self.__class__.__name__,
                    "function": self._validate_string_type_element.__name__,
                    }
        pattern_check = variable_to_check.get("pattern")
        is_valid_string = True
        if pattern_check is not None:
            is_valid_string = bool(re.match(pattern_check, input_data_value))
            warning_string = f"String variable must match pattern {variable_to_check['pattern']}."
            if not is_valid_string:
                om.add_warning(warning_string, f"{var_name=}", info_map)
                return is_valid_string

        minimum_length = variable_to_check.get("minimum_length")
        maximum_length = variable_to_check.get("maximum_length")
        if minimum_length is not None and maximum_length is not None:
            is_valid_string = variable_to_check["minimum_length"] <= len(input_data_value) <= \
                variable_to_check["maximum_length"]
            warning_string = f"String out length range [{minimum_length}, {maximum_length}]."
        elif minimum_length is not None:
            is_valid_string = variable_to_check["minimum_length"] <= len(input_data_value)
            warning_string = f"String length less than {minimum_length}."
        elif maximum_length is not None:
            is_valid_string = len(input_data_value) <= variable_to_check["maximum_length"]
            warning_string = f"String length more than {maximum_length}."

        if not is_valid_string:
            om.add_warning(warning_string, f"{var_name=}", info_map)

        return is_valid_string

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

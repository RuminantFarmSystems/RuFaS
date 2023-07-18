# !/usr/bin/env python3

from functools import reduce
import json
import re

import pandas as pd
from RUFAS.output_manager import OutputManager
from typing import Any, Dict, List

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

    def start_data_pipeline(self) -> None:
        """Organize metadata and input data processing pipeline"""
        self._load_metadata()
        self._load_data()
        start_simulation = self._validate_data()
        if not start_simulation:
            # TODO what actions to take if data is not valid?
            # need to trigger OM data dumping
            # need to stop simulation (what's the best way to do this?)
            pass

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

    def _check_variable_nested(self, variable_to_check: Dict[str, Any]) -> bool:
        """Checks if element currently being validated is nested.

        Parameters
        ----------
        variable_to_check : (Dict[str, Any])
            The corresponding value for the variable being checked.

        Returns
        -------
        bool
            True if variable_to_check has "object" as "type" in metadata. False otherwise.
        """
        non_nested_types = ["number", "string", "boolean", "array"]
        if variable_to_check["type"] in non_nested_types:
            is_nested = False
        elif variable_to_check["type"] == "object":
            is_nested = True
        else:
            is_nested = False
        return is_nested

    def _get_variable_type(self, variable_to_check: Dict[str, Any]) -> str:
        """_summary_

        Parameters
        ----------
        variable_to_check : Dict[str, Any]
            The corresponding value for the variable being checked.

        Returns
        -------
        str
            The type of the variable being checked.
        """
        return variable_to_check.get("type")

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

        property_map_kay : str
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
        element_heirarchy = element.split(".")
        variable_to_check = reduce(lambda d, key: d[key], element_heirarchy,
                                   self.__metadata["properties"][property_map_key])
        is_nested = self._check_variable_nested(element_heirarchy, variable_to_check)
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
            var_type = self._get_variable_type(variable_to_check)
            var_name = element_heirarchy[-1]
            input_data_value = reduce(lambda d, key: d[key], element_heirarchy, self.__pool[module_key])
            if var_type == "string":
                is_valid = self._validate_string_type_element(variable_to_check, var_name, input_data_value)
            elif var_type == "number":
                is_valid = self._validate_num_type_element(variable_to_check, var_name, input_data_value)
            elif var_type == "boolean":
                is_valid = self._validate_bool_type_element(input_data_value)
            elif var_type == "array":
                is_valid = self._validate_array_type_element(variable_to_check, var_name, input_data_value)
            else:
                return False

            if is_valid:
                return True
            else:
                is_fixed = self._fix_data(module_key, element_heirarchy)
                return is_fixed

    def _validate_array_type_element(self,
                                     variable_to_check: Dict[str, Any],
                                     var_name: str,
                                     input_data_value: list) -> bool:
        """
        Validates a __pool element when the element is an array.

        Parameters
        ----------
        variable_to_check : str
            A dictionary with the metadata validation guidelines.

        var_name : str
            The name of the variable being checked.

        value : Union[int, str, bool, list]
            The value of the variable being checked.

        Returns
        -------
        bool
            Returns True if variable meets guidelines; otherwise False.
        """
        info_map = {"class": self.__class__.__name__,
                    "function": self._validate_array_type_element.__name__,
                    }
        is_maximum_length = variable_to_check.get("maximum_length")
        is_minimum_length = variable_to_check.get("minimum_length")
        if is_maximum_length and is_minimum_length:
            is_in_range = variable_to_check["minimum_length"] <= len(input_data_value) <= \
                variable_to_check["maximum_length"]
            if not is_in_range:
                om.add_warning("Array out of length range.", f"{var_name=}", info_map)
            return is_in_range
        elif is_minimum_length:
            is_in_range = variable_to_check["minimum_length"] <= len(input_data_value)
            if not is_in_range:
                om.add_warning("Array out of length range.", f"{var_name=}", info_map)
            return is_in_range
        elif is_maximum_length:
            is_in_range = len(input_data_value) <= variable_to_check["maximum_length"]
            if not is_in_range:
                om.add_warning("Array out of length range.", f"{var_name=}", info_map)
            return is_in_range
        else:
            return False

    def _validate_bool_type_element(self, input_data_value: bool) -> bool:
        """
        Validates a __pool boolean element.

        Parameters
        ----------
        value : Union[int, str, bool, list]
            The value of the variable being checked.

        Returns
        -------
        bool
            Returns True if variable meets guidelines; otherwise False.
        """
        return input_data_value in (True, False)

    def _validate_num_type_element(self,
                                   variable_to_check: Dict[str, Any],
                                   var_name: str,
                                   input_data_value: int) -> bool:
        """
        Validates a __pool number element.

        Parameters
        ----------
        variable_to_check : str
            A dictionary with the metadata validation guidelines.

        var_name : str
            The name of the variable being checked.

        value : int
            The value of the integer variable being checked.

        Returns
        -------
        bool
            Returns True if variable meets guidelines; otherwise False.
        """
        info_map = {"class": self.__class__.__name__,
                    "function": self._validate_num_type_element.__name__,
                    }
        is_minimum_check = variable_to_check.get("minimum")
        is_maximum_check = variable_to_check.get("maximum")
        if is_minimum_check and is_maximum_check:
            is_in_range = variable_to_check["minimum"] <= input_data_value <= variable_to_check["maximum"]
            if not is_in_range:
                om.add_warning("Value out of range.", f"{var_name=}", info_map)
            return is_in_range
        elif is_minimum_check:
            is_in_range = variable_to_check["minimum"] <= input_data_value
            if not is_in_range:
                om.add_warning("Value out of range.", f"{var_name=}", info_map)
            return is_in_range
        elif is_maximum_check:
            is_in_range = input_data_value <= variable_to_check["maximum"]
            if not is_in_range:
                om.add_warning("Value out of range.", f"{var_name=}", info_map)
            return is_in_range
        else:
            return True

    def _validate_string_type_element(self,
                                      variable_to_check: Dict[str, Any],
                                      var_name: str,
                                      input_data_value: str) -> bool:
        """
        Validates a __pool string element.

        Parameters
        ----------
        variable_to_check : str
            A dictionary with the metadata validation guidelines.

        var_name : str
            The name of the variable being checked.

        value : str
            The value of the string variable being checked.

        Returns
        -------
        bool
            Returns True if variable meets guidelines; otherwise False.
        """
        info_map = {"class": self.__class__.__name__,
                    "function": self._validate_string_type_element.__name__,
                    }
        is_pattern_check = variable_to_check.get("pattern")
        is_minimum_length = variable_to_check.get("minimum_length")
        is_maximum_length = variable_to_check.get("maximum_length")
        is_valid_string = True
        if is_pattern_check:
            is_valid_string = bool(re.match(variable_to_check["pattern"], input_data_value))
            if not is_valid_string:
                om.add_warning(f"String variable must match pattern {variable_to_check['pattern']}.",
                               f"{var_name=}",
                               info_map)
                return is_valid_string
        if is_minimum_length and is_maximum_length:
            is_valid_string = variable_to_check["minimum_length"] <= len(input_data_value) <= \
                variable_to_check["maximum_length"]
            if not is_valid_string:
                om.add_warning("String out length range.", f"{var_name=}", info_map)
                return False
        elif is_minimum_length:
            is_valid_string = variable_to_check["minimum_length"] <= len(input_data_value)
            if not is_valid_string:
                om.add_warning("String out length range.", f"{var_name=}", info_map)
                return False
        elif is_maximum_length:
            is_valid_string = len(input_data_value) <= variable_to_check["maximum_length"]
            if not is_valid_string:
                om.add_warning("String out length range.", f"{var_name=}", info_map)
                return False

        return is_valid_string

    def _fix_data(self, module_key: str, property_map_key: str, element_hierarchy: List[str]) -> bool:
        """
        Attempt to fix the invalid data.
        Return True if the data is fixed, False for critical data

        Parameters
        ----------
        variable_path : List[str]
            The path to reach the variable of interest.

        Returns
        -------
        bool
            True if the data is fixed, False for critical data.
        """
        info_map = {"class": self.__class__.__name__,
                    "function": self._fix_data.__name__,
                    }

        current_metadata: dict = self.__metadata['properties'][property_map_key]
        for metadata_key in element_hierarchy:
            current_metadata = current_metadata[metadata_key]

        if 'default' in current_metadata.keys():
            current_pool = self.__pool[module_key]
            for pool_key in element_hierarchy[:-1]:
                current_pool = current_pool[pool_key]

            current_pool[element_hierarchy[-1]] = current_metadata['default']
            om.add_warning("Data fixed", f"Invalid data fixed: {element_hierarchy[-1]} => {current_metadata['default']}",
                           info_map)
            return True

        else:
            return False

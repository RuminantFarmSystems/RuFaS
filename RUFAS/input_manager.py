# !/usr/bin/env python3

from functools import reduce
import json
import re

import pandas as pd
from RUFAS.output_manager import OutputManager
from typing import Any, Dict, List, Optional


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
            True if data is valid, otherwise False.
        """
        self._load_metadata(metadata_path)
        is_input_data_valid = self._validate_data_and_add_to_pool(eager_termination)
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

    def _load_data_from_json(self, file_path: str) -> Dict[str, Any]:
        """
        Loads data from input json file.

        Parameters
        ----------
        file_path : str
            Path to the input file to load.

        Returns
        -------
        Dict[str, Any]
            The data dictionary loaded from the json file.
        """
        info_map = {"class": self.__class__.__name__,
                    "function": self._load_data_from_json.__name__,
                    }
        om.add_log("open_json_file", f"Attempting to open {file_path}.", info_map)
        try:
            with open(file_path) as json_file:
                data = json.load(json_file)
                om.add_log("load_data_successful", f"Successfully loaded data from {file_path}.", info_map)
                return data
        except Exception as e:
            raise e

    def _load_data_from_csv(self, file_path: str) -> Dict[str, Any]:
        """
        Loads data from input csv file.

        Parameters
        ----------
        file_path : str
            Path to the input file to load.

        Returns
        -------
        Dict[str, Any]
            The data dictionary loaded from the json file.
        """
        info_map = {"class": self.__class__.__name__,
                    "function": self._load_data_from_csv.__name__,
                    }
        om.add_log("open_csv_file", f"Attempting to open {file_path}.", info_map)
        try:
            with open(file_path, "r") as csv_file:
                data_frame = pd.read_csv(csv_file)
                data_dict = {column: data_frame[column].tolist() for column in data_frame.columns}
                if not data_frame.empty:
                    om.add_log("load_data_successful",
                               f"Successfully loaded data from {file_path}.",
                               info_map)
                return data_dict
        except Exception as e:
            raise e

    def _validate_data_and_add_to_pool(self, eager_termination: bool) -> bool:
        """
        Validates data from input files and adds data to pool if valid.

        Parameters
        ----------
        eager_termination : bool
            If True, the process will be terminated as soon as finding invalid data and failing to fix it.
            If False, the process will be terminated after going through and validating the entire data,
            if invalid data is found.

        Returns
        -------
        bool
            True if data is valid, otherwise False.
        """
        info_map = {"class": self.__class__.__name__,
                    "function": self._validate_data_and_add_to_pool.__name__,
                    }
        valid_items_counter = 0
        invalid_items_counter = 0
        total_items_counter = 0

        for file_blob_key, file_details in self.__metadata["files"].items():
            file_path = file_details["path"]
            data_type_to_loader_map = {"json": self._load_data_from_json,
                                       "csv": self._load_data_from_csv}
            try:
                data_loader = data_type_to_loader_map[file_details["type"]]
                data = data_loader(file_path)
            except KeyError:
                raise KeyError(f"Faulty data type in {file_blob_key}, only CSV and JSON are supported.")

            properties_blob_key = file_details["properties"]
            properties = self.__metadata["properties"][properties_blob_key]
            for property in properties.keys():
                total_items_counter += 1
                is_valid_element = self._validate_element([property], properties_blob_key, data,
                                                          eager_termination)
                if is_valid_element:
                    valid_items_counter += 1
                    self.__pool[file_blob_key] = data
                else:
                    if not eager_termination:
                        invalid_items_counter += 1
                    else:
                        return False

        om.add_log("Total Valid Items", f"{valid_items_counter=}", info_map)
        om.add_log("Total Checked Items", f"{total_items_counter=}", info_map)
        om.add_log("Total Invalid Critical Items", f"{invalid_items_counter=}", info_map)
        return invalid_items_counter == 0

    def _validate_element(self, element_hierarchy: List[str], properties_blob_key: str,
                          input_data: Dict[str, Any], eager_termination: bool) -> bool:
        """
        Perform data validation checks.

        Parameters
        ----------
        element_hierarchy : List[str]
            A list of strings representing the path to the data being validated.

        properties_blob_key : str
            The metadata properties section keyword for the data input file being checked.

        input_data : Dict[str, Any]
            A buffer dictionary that holds the input data for validation and fixing.

        eager_termination : bool
            If true, the process will be terminated upon finding invalid data.

        Returns
        -------
        bool
            True if the data is valid, False otherwise.
        """
        info_map = {"class": self.__class__.__name__,
                    "function": self._validate_element.__name__,
                    }
        variable_properties = reduce(lambda d, key: d[key], element_hierarchy,
                                     self.__metadata["properties"][properties_blob_key])
        var_type = variable_properties["type"]
        is_nested = var_type == "object"
        if is_nested:
            children_status: Dict[str, bool] = {}
            false_counter = 0
            for nested_key in variable_properties.keys():
                element_hierarchy.append(nested_key)
                child_status = self._validate_element(element_hierarchy, properties_blob_key,
                                                      input_data, eager_termination)
                if eager_termination and not child_status:
                    return False
                element_path = ".".join(element_hierarchy)
                children_status[element_path] = child_status
                if not child_status:
                    om.add_warning("Invalid nested element found", f"{element_path}", info_map)
                    false_counter += 1
                element_hierarchy.remove(nested_key)
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
                input_data_value = reduce(lambda d, key: d[key], element_hierarchy, input_data)
            except KeyError:
                raise KeyError(f"Key {var_name} not found in input data")

            type_validation_dict = {"string": self._validate_string_type_element,
                                    "number": self._validate_num_type_element,
                                    "array": self._validate_array_type_element,
                                    "bool": self._validate_bool_type_element, }

            try:
                validity_checker = type_validation_dict[var_type]
                is_valid = validity_checker(variable_properties, var_name, input_data_value)
            except KeyError:
                raise KeyError(f"Invalid type {var_type}: Element must be type number, array, string, or bool")

            if is_valid:
                return True
            else:
                is_fixed = self._fix_data(variable_properties, element_hierarchy, input_data)
                return is_fixed

    def _validate_array_type_element(self, variable_properties: Dict[str, Any], var_name: str,
                                     input_data_value: list) -> bool:
        """Validates an input data element of type array."""
        info_map = {"class": self.__class__.__name__,
                    "function": self._validate_array_type_element.__name__,
                    }
        maximum_length = variable_properties.get("maximum_length")
        minimum_length = variable_properties.get("minimum_length")
        is_in_range = True
        if minimum_length is not None:
            is_in_range = variable_properties["minimum_length"] <= len(input_data_value)
            if not is_in_range:
                warning_string = f"Array length less than {minimum_length}."
                om.add_warning(warning_string, f"{var_name=}", info_map)
                return is_in_range
        if maximum_length is not None:
            is_in_range = len(input_data_value) <= variable_properties["maximum_length"]
            if not is_in_range:
                warning_string = f"Array length more than {maximum_length}."
                om.add_warning(warning_string, f"{var_name=}", info_map)

        return is_in_range

    def _validate_num_type_element(self, variable_properties: Dict[str, Any], var_name: str,
                                   input_data_value: float) -> bool:
        """Validates an input data number element."""
        info_map = {"class": self.__class__.__name__,
                    "function": self._validate_num_type_element.__name__,
                    }
        minimum_value = variable_properties.get("minimum")
        maximum_value = variable_properties.get("maximum")
        is_in_range = True
        if minimum_value is not None:
            is_in_range = minimum_value <= input_data_value
            if not is_in_range:
                warning_string = f"Value less than {minimum_value}."
                om.add_warning(warning_string, f"{var_name=}", info_map)
                return is_in_range
        if maximum_value is not None:
            is_in_range = input_data_value <= maximum_value
            if not is_in_range:
                warning_string = f"Value greater than {maximum_value}."
                om.add_warning(warning_string, f"{var_name=}", info_map)

        return is_in_range

    def _validate_string_type_element(self, variable_properties: Dict[str, Any], var_name: str,
                                      input_data_value: str) -> bool:
        """Validates an input data string element."""
        info_map = {"class": self.__class__.__name__,
                    "function": self._validate_string_type_element.__name__,
                    }
        pattern_check = variable_properties.get("pattern")
        is_valid_string = True
        if pattern_check is not None:
            is_valid_string = bool(re.match(pattern_check, input_data_value))
            if not is_valid_string:
                warning_string = f"String variable must match pattern {variable_properties['pattern']}."
                om.add_warning(warning_string, f"{var_name=}", info_map)
                return is_valid_string

        minimum_length = variable_properties.get("minimum_length")
        maximum_length = variable_properties.get("maximum_length")
        if minimum_length is not None:
            is_valid_string = variable_properties["minimum_length"] <= len(input_data_value)
            if not is_valid_string:
                warning_string = f"String length less than {minimum_length}."
                om.add_warning(warning_string, f"{var_name=}", info_map)
                return is_valid_string
        if maximum_length is not None:
            is_valid_string = len(input_data_value) <= variable_properties["maximum_length"]
            if not is_valid_string:
                warning_string = f"String length more than {maximum_length}."
                om.add_warning(warning_string, f"{var_name=}", info_map)

        return is_valid_string

    def _validate_bool_type_element(self, variable_properties: Dict[str, Any], var_name: str,
                                    input_data_value: bool) -> bool:
        """Validates an input data bool element."""
        return input_data_value in (True, False)

    def _fix_data(self, variable_properties: dict[str, Any], element_hierarchy: List[str],
                  input_data: dict[str, Any]) -> bool:
        """
        Attempt to fix the invalid data.

        Parameters
        ----------
        variable_properties : dict[str, Any]
            The properties for the variable of interest.

        element_hierarchy: List[str]
            A list of strings indicating the path to reach the variable of interest in self.__metadata and self.__pool.

        input_data: dict[str, Any]
            A buffer dictionary that holds the input data for validation and fixing.

        Returns
        -------
        bool
            True if the data is fixed, False otherwise.
        """
        info_map = {"class": self.__class__.__name__,
                    "function": self._fix_data.__name__,
                    }

        if 'default' not in variable_properties.keys():
            return False
        variable_parent = reduce(lambda d, key: d[key], element_hierarchy[:-1],
                                 input_data)
        variable_parent[element_hierarchy[-1]] = variable_properties['default']
        om.add_warning("Data fixed",
                       f"Invalid data fixed: {element_hierarchy[-1]} => {variable_properties['default']}",
                       info_map)
        return True

    def get_data(self, data_address: str) -> Optional[Any]:
        """
        Get the requested data from the pool

        Parameters
        ----------
        data_address : str
            The address of the requested data.

        Returns
        -------
        Any
            The requested data if found.

        Raises
        -------
        KeyError
            If the requested data is not found.

        Examples
        -------
        >>> InputManager.get_data('animal.herd.calf_num')
        This will return the value of `calf_num` of the `herd` section in the `animal` module.
        """
        info_map = {"class": self.__class__.__name__,
                    "function": self.get_data.__name__,
                    }

        element_hierarchy = data_address.split('.')

        try:
            data_value = reduce(lambda d, key: d[key], element_hierarchy,
                                self.__pool)
            return data_value

        except KeyError as key_error:
            invalid_key = str(key_error).strip("\'")
            parent_address = str(data_address.split("." + invalid_key)[0])

            om.add_warning("Data not found:", f"Cannot find \"{data_address}\", "
                                              f"\"{parent_address}\" does not have attribute \"{invalid_key}\".",
                           info_map)

            raise KeyError(f"Data not found: Cannot find \"{data_address}\", "
                           f"\"{parent_address}\" does not have attribute \"{invalid_key}\".")

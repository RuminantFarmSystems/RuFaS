# !/usr/bin/env python3
from __future__ import annotations

import json
import re
from copy import deepcopy
from functools import reduce
from typing import Any, Dict, List, Union, Tuple, Callable

import numpy as np
import pandas as pd

from RUFAS.output_manager import OutputManager

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
        self.counter = ElementsCounter()

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
        is_input_data_valid = self._populate_pool(eager_termination)
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

    def _populate_pool(self, eager_termination: bool) -> bool:
        """
        Loads input files, runs validations on the data from the input files, attempts to fix invalid data,
        then adds data to the pool.

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
                    "function": self._populate_pool.__name__,
                    }

        data_type_to_loader_map = {"json": self._load_data_from_json,
                                   "csv": self._load_data_from_csv}

        for file_blob_key, file_details in self.__metadata["files"].items():
            file_path = file_details["path"]

            try:
                file_type = file_details["type"]
                data_loader = data_type_to_loader_map[file_details["type"]]
                input_data = data_loader(file_path)
            except KeyError:
                raise KeyError(f"Faulty data type in {file_blob_key},"
                               f"supported types are: {data_type_to_loader_map.keys()}")

            properties_blob_key = file_details["properties"]
            properties = self.__metadata["properties"][properties_blob_key]
            for first_level_prop in properties:
                if file_type == "json":
                    is_prop_acceptable = self._validate_json_element(first_level_prop,
                                                                     properties_blob_key,
                                                                     input_data)
                elif file_type == "csv":
                    is_prop_acceptable = self._validate_csv_element(first_level_prop,
                                                                    properties_blob_key,
                                                                    input_data)
                else:
                    raise KeyError(f"Faulty data type in {file_blob_key},"
                                   f"supported types are: {data_type_to_loader_map.keys()}")

                if is_prop_acceptable:
                    self.__pool[file_blob_key] = input_data
                elif eager_termination:
                    return False

        om.add_log("Input Manager Validation Statistics", f"{self.counter}", info_map)

        return self.counter.invalid_elements == 0

    def _filter_input_data_by_metadata(self, input_data: Dict[str, Any],
                                       metadata_properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter input data dictionary based on provided metadata properties.

        This function removes key-value pairs from the input data dictionary (input_data) if
        the corresponding keys are not present in the metadata properties dictionary
        (metadata_properties). Nested dictionaries are processed recursively.

        Parameters:
        -----------
        input_data : dict
            The input data dictionary to be filtered.

        metadata_properties : Dict[str, Any]
            The dictionary containing metadata properties used as a filter for input_data.
        """
        filtered_input_data = {}
        for key, value in input_data.items():
            if key in metadata_properties:
                if isinstance(metadata_properties[key], dict) and isinstance(value, dict):
                    nested_input_data = self._filter_input_data_by_metadata(value, metadata_properties[key])
                    if nested_input_data:
                        filtered_input_data[key] = nested_input_data
                else:
                    filtered_input_data[key] = value

        return filtered_input_data

    def _validate_input_type_dynamic(self, variable_properties: Dict[str, Any],
                                     variable_path: List[str | int],
                                     input_data_value: Any) -> bool:
        """
        Validates the input data value based on its specified dynamic type.

        Parameters
        ----------
        variable_properties : Dict[str, Any]
            A dictionary containing properties relevant to the validation.
        input_data_value : Any
            The input data value to be validated.

        Returns
        -------
        bool
            True if the input data value is valid for the specified type, False otherwise.

        Raises
        ------
        KeyError
            If an invalid type is provided in the variable_properties or if "type" key is missing.

        Notes
        ------
        This function determines the type of validation needed based on the 'type' property in variable_properties.
        It dynamically selects the appropriate validator based on the determined type and delegates the validation
        process to that validator function. If the determined type is not recognized or if "type" key is missing,
        a KeyError is raised.

        Example
        --------
        variable_properties = {"type": "string", "min_length": 3, "max_length": 10}
        var_name = "name"
        input_data_value = "John Doe"
        is_valid = validate_input_type_dynamic(variable_properties, var_name, input_data_value)
        if is_valid:
            print(f"{var_name} is a valid {variable_properties['type']}.")
        else:
            print(f"{var_name} is not a valid {variable_properties['type']}.")
        """
        if "type" not in variable_properties:
            raise KeyError(f"Missing 'type' key in variable_properties: {variable_properties}")
        var_type = variable_properties["type"]

        data_type_to_validator_map = {
            "string": self._validate_str_type,
            "number": self._validate_num_type,
            "bool": self._validate_bool_type,
            "object": self._validate_object_type,
            "array": self._validate_array_type,
        }

        if var_type not in data_type_to_validator_map:
            raise KeyError(f"Invalid type {var_type}: Element must be type "
                           f"{list(data_type_to_validator_map.keys())}")

        return data_type_to_validator_map[var_type](variable_path, variable_properties, input_data_value)

    def _validate_csv_element(self, first_level_prop: str, properties_blob_key: str,
                              input_data: Dict[str, Any]) -> bool:
        """
        Receive data loaded from csv input file and then validates each row element in the csv column it's sent.

        It attempts to fix any invalid elements and tracks the number of valid, invalid, fixed,
        and total elements from the input file are checked.

        Parameters
        ----------
        first_level_prop : str
            The name of the csv data element being validated.

        properties_blob_key : str
            The metadata properties section keyword for the data input file being checked.

        input_data : Dict[str, Any]
            A buffer dictionary that holds the input data for validation and fixing.

        """
        blob_key_data = self.__metadata["properties"][properties_blob_key]
        variable_properties = self._get_nested_dict_value(self.__metadata["properties"][properties_blob_key],
                                                          [first_level_prop])

        column_data = input_data[first_level_prop]

        for idx in range(len(column_data)):
            is_sub_element_acceptable = self._validate_input_type_dynamic(variable_properties,
                                                                          [first_level_prop, idx],
                                                                          input_data)
            if not is_sub_element_acceptable:
                return False

        return True

    def _validate_json_element(self, first_level_prop: str, properties_blob_key: str,
                               input_data: Dict[str, Any]) -> bool:
        """
        Validate an input data element extracted from a json file.

        Parameters
        ----------
        first_level_prop : str
            The name of the first level property in the metadata and input data, counting from the top.
        properties_blob_key : str
            The metadata properties section keyword for the data input file being checked.
        input_data : Dict[str, Any]
            A buffer dictionary that holds the input data for validation and fixing.

        Returns
        -------
        bool
            True if the element was valid or fixed, False otherwise.
        """

        variable_properties = self._get_nested_dict_value(
            self.__metadata["properties"][properties_blob_key], [first_level_prop]
        )

        return self._validate_input_type_dynamic(variable_properties, [first_level_prop], input_data)

    @staticmethod
    def _get_nested_dict_value(input_data: List | Dict[str, Any], keys: List[str | int]) -> Any:
        """
        Get a value from a nested dictionary by following the keys in the input_data dictionary.

        Parameters
        ----------
        input_data : List | Dict[str, Any]
            The list or dictionary to get the value from.
        keys : List[str | int]
            The keys to follow in the dictionary to get the value. When the key is an int, it is used to index a list.

        Returns
        -------
        Any
            The value from the nested dictionary.

        Raises
        ------
        KeyError
            If the key is not found in the input_data dictionary.
        IndexError
            If the index is not found in the input_data list.

        Examples
        --------
        >>> InputManager._get_nested_dict_value({"a": {"b": 1}}, ["a", "b"])
        1
        >>> InputManager._get_nested_dict_value({"a": {"b": {"c": [1, 2, 3]}}}, ["a", "b", "c", 1])
        2
        >>> InputManager._get_nested_dict_value({"a": {"b": {"c": [1, 2, 3]}}}, ["a", "b", "c", 3])
        KeyError: 3
        """

        for key in keys:
            if isinstance(input_data, dict) or isinstance(input_data, list):
                input_data = input_data[key]
            else:
                return input_data
        return input_data

    @staticmethod
    def _convert_variable_path_to_str(variable_path: List[str | int]) -> str:
        """
        Convert a variable path list to a string.

        Parameters
        ----------
        variable_path : List[str | int]
            The variable path to convert.

        Returns
        -------
        str
            The variable path as a string.

        Examples
        --------
        >>> InputManager._convert_variable_path_to_str(["a", "b", 1])
        "a.b.[1]"
        >>> InputManager._convert_variable_path_to_str(["a", "b", "c"])
        "a.b.c"
        >>> InputManager._convert_variable_path_to_str(["a", "b", "c", 0, 1])
        "a.b.c.[0].[1]"
        """

        elems = []
        for elem in variable_path:
            if isinstance(elem, int):
                elems.append(f"[{elem}]")
            else:
                elems.append(elem)
        return ".".join(elems)

    def _handle_container_error(self, error_msg: str, variable_path: List[str | int],
                                variable_properties: Dict[str, Any],
                                input_data: Dict[str, Any], ) -> bool:
        """
        Replace an invalid array or object data element with a default value if available or log an error.

        After replacing the invalid element, the function will attempt to validate the element again to
        make sure the default value is valid.

        Parameters
        ----------
        error_msg : str
            The error message to log.
        variable_path : List[str | int]
            The path to the variable by following the keys in the input_data dictionary.
        variable_properties : Dict[str, Any]
            The properties for the variable of interest.
        input_data : Dict[str, Any]
            A reference to the input data dictionary to enable in-place fixing.

        Returns
        -------
        bool
            True if the data was fixed successfully, False otherwise.
        """

        info_map = {
            "class": self.__class__.__name__,
            "function": self._handle_container_error.__name__,
        }
        variable_path_str = self._convert_variable_path_to_str(variable_path)
        element_to_validate = self._get_nested_dict_value(input_data, variable_path)
        om.add_warning(error_msg, f"{variable_path_str} = {element_to_validate}", info_map)

        is_variable_fixed = self._fix_data(variable_properties, variable_path, input_data)
        if is_variable_fixed:
            return self._validate_input_type_dynamic(variable_properties, variable_path, input_data)

        om.add_error("Invalid unfixable element found", f"{variable_path_str} = {element_to_validate}", info_map)
        self.counter.increment("total_elements")
        self.counter.increment("invalid_elements")
        return False

    def _revalidate_primitive_element_after_fix(self, variable_path: List[str | int],
                                                variable_properties: Dict[str, Any],
                                                input_data: Dict[str, Any],
                                                primitive_type_specific_validators: List[
                                                    Callable[[Any, Dict[str, Any]], Tuple[bool, str]]]) -> bool:
        """
        Revalidate a primitive data element after fixing it.

        Parameters
        ----------
        variable_path : List[str | int]
            The path to the variable by following the keys in the input_data dictionary.
        variable_properties : Dict[str, Any]
            The properties for the variable of interest.
        input_data : Dict[str, Any]
            A reference to the input data dictionary to enable in-place fixing.
        primitive_type_specific_validators : List[Callable[[Any, Dict[str, Any]], Tuple[bool, str]]]
            A list of functions to use for validating the input data element.

        Returns
        -------
        bool
            True if the element was valid or fixed, False otherwise.
        """

        element_to_validate = self._get_nested_dict_value(input_data, variable_path)
        variable_path_str = self._convert_variable_path_to_str(variable_path)
        info_map = {
            "class": self.__class__.__name__,
            "function": self._revalidate_primitive_element_after_fix.__name__,
        }
        for validator in primitive_type_specific_validators:
            is_valid, error_msg = validator(element_to_validate, variable_properties)
            if not is_valid:
                om.add_error("Fixed element is still invalid",
                             f"{variable_path_str} = {element_to_validate}",
                             info_map)
                self.counter.increment("invalid_elements")
                return False

        self.counter.increment("fixed_elements")
        return True

    def _validate_primitive_type_with_revalidation(self, variable_path: List[str | int],
                                                   variable_properties: Dict[str, Any],
                                                   input_data: Dict[str, Any],
                                                   primitive_type_specific_validators: List[
                                                       Callable[[Any, Dict[str, Any]], Tuple[
                                                           bool, str]]]) -> bool:
        """
        Validate input data of primitive type (string, number, boolean) with revalidation of the fixed data.

        Parameters
        ----------
        variable_path : List[str | int]
            The path to the variable by following the keys in the input_data dictionary.
        variable_properties : Dict[str, Any]
            The properties for the variable of interest.
        input_data : Dict[str, Any]
            A reference to the input data dictionary to enable in-place fixing.
        primitive_type_specific_validators : List[Callable[[Any, Dict[str, Any]], Tuple[bool, str]]]
            A list of functions to use for validating the input data element.

        Returns
        -------
        bool
            True if the element was valid or fixed, False otherwise.
        """

        self.counter.increment("total_elements")
        element_to_validate = self._get_nested_dict_value(input_data, variable_path)
        variable_path_str = self._convert_variable_path_to_str(variable_path)
        info_map = {
            "class": self.__class__.__name__,
            "function": self._validate_primitive_type_with_revalidation.__name__,
        }
        for validator in primitive_type_specific_validators:
            is_valid, error_msg = validator(element_to_validate, variable_properties)
            if is_valid:
                continue
            om.add_warning(error_msg, f"{variable_path_str} = {element_to_validate}", info_map)
            is_variable_fixable = self._fix_data(variable_properties, variable_path, input_data)
            if is_variable_fixable:
                return self._revalidate_primitive_element_after_fix(variable_path, variable_properties, input_data,
                                                                    primitive_type_specific_validators)
            om.add_error("Invalid, unfixable element found", f"{variable_path_str} = {element_to_validate}", info_map)
            self.counter.increment("invalid_elements")
            return False

        self.counter.increment("valid_elements")
        return True

    @staticmethod
    def _is_bool_value(variable_value: Any, variable_properties: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check if the variable value is a boolean.

        Parameters
        ----------
        variable_value : Any
            The value of the variable to check.
        variable_properties : Dict[str, Any]
            The properties for the variable of interest.

        Returns
        -------
        Tuple[bool, str]
            A tuple containing a boolean indicating if the check passed and a string containing the reason for failure.

        """

        if type(variable_value) is not bool:
            return False, "Bool variable is not a boolean"
        return True, ""

    def _validate_bool_type(self, variable_path: List[str | int],
                            variable_properties: Dict[str, Any],
                            input_data: Dict[str, Any]) -> bool:
        """
        Validate an input data boolean element.

        Parameters
        ----------
        variable_path : List[str | int]
            The path to the variable by following the keys in the input_data dictionary.
        variable_properties : Dict[str, Any]
            The properties for the variable of interest.
        input_data : Dict[str, Any]
            A reference to the input data dictionary to enable in-place fixing.

        Returns
        -------
        bool
            True if the input data value is valid for the specified type, False otherwise.
        """

        return self._validate_primitive_type_with_revalidation(variable_path, variable_properties,
                                                               input_data, [self._is_bool_value])

    @staticmethod
    def _is_numeric_value(variable_value: Any, variable_properties: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check if the variable value is a number and not NaN.

        Parameters
        ----------
        variable_value : Any
            The value of the variable to check.
        variable_properties : Dict[str, Any]
            The properties for the variable of interest.

        Returns
        -------
        Tuple[bool, str]
            A tuple containing a boolean indicating if the check passed and a string containing the reason for failure.
        """

        if not type(variable_value) in (int, float) or np.isnan(variable_value):
            return False, "Value is not a number"
        return True, ""

    @staticmethod
    def _check_num_lower_bound(variable_value: int | float,
                               variable_properties: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check if the variable value is greater than the minimum value.

        Parameters
        ----------
        variable_value : int | float
            The value of the variable to check.
        variable_properties : Dict[str, Any]
            The properties for the variable of interest.

        Returns
        -------
        Tuple[bool, str]
            A tuple containing a boolean indicating if the check passed and a string containing the reason for failure.
        """

        if "minimum" in variable_properties and variable_value < variable_properties["minimum"]:
            return False, "Value less than minimum"
        return True, ""

    @staticmethod
    def _check_num_upper_bound(variable_value: int | float,
                               variable_properties: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check if the variable value is less than the maximum value.

        Parameters
        ----------
        variable_value : int | float
              The value of the variable to check.
        variable_properties : Dict[str, Any]
              The properties for the variable of interest.

        Returns
        -------
        Tuple[bool, str]
              A tuple containing a boolean indicating if the check passed and a string containing the reason for
              failure.
        """

        if "maximum" in variable_properties and variable_value > variable_properties["maximum"]:
            return False, "Value greater than maximum"
        return True, ""

    def _validate_num_type(self, variable_path: List[str | int],
                           variable_properties: Dict[str, Any],
                           input_data: Dict[str, Any]) -> bool:
        """
        Validate an input data element of type number.

        Parameters
        ----------
        variable_properties : Dict[str, Any]
            The properties for the variable of interest.
        variable_path : List[str | int]
            The path to the variable by following the keys in the input_data dictionary.
        input_data : Dict[str, Any]
            A reference to the input data dictionary to enable in-place fixing.

        Returns
        -------
        bool
            True if the element was valid or fixed, False otherwise.
        """

        primitive_type_specific_validators = [
            self._is_numeric_value,
            self._check_num_lower_bound,
            self._check_num_upper_bound,
        ]

        return self._validate_primitive_type_with_revalidation(variable_path, variable_properties,
                                                               input_data, primitive_type_specific_validators)

    @staticmethod
    def _is_str_value(variable_value: Any, variable_properties: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check if the variable value is a string.

        Parameters
        ----------
        variable_value : Any
            The value of the variable to check.
        variable_properties : Dict[str, Any]
            The properties for the variable of interest.

        Returns
        -------
        Tuple[bool, str]
            A tuple containing a boolean indicating if the check passed and a string containing the reason for failure.

        """

        if type(variable_value) is not str:
            return False, "String variable is not a string."
        return True, ""

    @staticmethod
    def _check_str_len_lower_bound(variable_value: str,
                                   variable_properties: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check if the variable value is greater than the minimum length.

        Parameters
        ----------
        variable_value : str
            The value of the variable to check.
        variable_properties : Dict[str, Any]
            The properties for the variable of interest.

        Returns
        -------
        Tuple[bool, str]
            A tuple containing a boolean indicating if the check passed and a string containing the reason for failure.
        """

        if "minimum_length" in variable_properties and len(variable_value) < variable_properties["minimum_length"]:
            return False, "String length less than minimum."
        return True, ""

    @staticmethod
    def _check_str_len_upper_bound(variable_value: str,
                                   variable_properties: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check if the variable value is less than the maximum length.

        Parameters
        ----------
        variable_value : str
            The value of the variable to check.
        variable_properties : Dict[str, Any]
            The properties for the variable of interest.

        Returns
        -------
        Tuple[bool, str]
            A tuple containing a boolean indicating if the check passed and a string containing the reason for failure.
        """

        if "maximum_length" in variable_properties and len(variable_value) > variable_properties["maximum_length"]:
            return False, "String length greater than maximum."
        return True, ""

    @staticmethod
    def _check_str_pattern_match(variable_value: str,
                                 variable_properties: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check if the variable value matches the specified pattern.

        Parameters
        ----------
        variable_value : str
              The value of the variable to check.
        variable_properties : Dict[str, Any]
              The properties for the variable of interest.

        Returns
        -------
        Tuple[bool, str]
              A tuple containing a boolean indicating if the check passed and a string containing the reason for
              failure.
        """

        if "pattern" in variable_properties and not re.fullmatch(variable_properties["pattern"], variable_value):
            return False, "String does not match pattern."
        return True, ""

    def _validate_str_type(self, variable_path: List[str | int],
                           variable_properties: Dict[str, Any],
                           input_data: Dict[str, Any]) -> bool:
        """
        Validate an input data element of type string.

        Parameters
        ----------
        variable_path : List[str | int]
            The path to the variable by following the keys in the input_data dictionary.
        variable_properties : Dict[str, Any]
            The properties for the variable of interest.
        input_data : Dict[str, Any]
            A reference to the input data dictionary to enable in-place fixing.

        Returns
        -------
        bool
            True if the element was valid or fixed, False otherwise.
        """

        type_specific_validators = [
            self._is_str_value,
            self._check_str_len_lower_bound,
            self._check_str_len_upper_bound,
            self._check_str_pattern_match,
        ]

        return self._validate_primitive_type_with_revalidation(variable_path, variable_properties,
                                                               input_data, type_specific_validators)

    @staticmethod
    def _is_object_value(variable_value: Dict, variable_properties: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check if the variable value is a dictionary.

        Parameters
        ----------
        variable_value : Any
            The value of the variable to check.
        variable_properties : Dict[str, Any]
            The properties for the variable of interest.

        Returns
        -------
        Tuple[bool, str]
            A tuple containing a boolean indicating if the check passed and a string containing the reason for failure.

        """

        if type(variable_value) is not dict:
            return False, "Object variable is not a dictionary."
        return True, ""

    def _validate_object_type(self, variable_path: List[str | int],
                              variable_properties: Dict[str, Any],
                              input_data: Dict[str, Any]) -> bool:
        """
        Validate an input data element of type object.

        Parameters
        ----------
        variable_path : List[str | int]
            The path to the variable by following the keys in the input_data dictionary.
        variable_properties : Dict[str, Any]
            The properties for the variable of interest.
        input_data : Dict[str, Any]
            A reference to the input data dictionary to enable in-place fixing.

        Returns
        -------
        bool
            True if the element was valid or fixed, False otherwise.
        """

        object_container_validators = [
            self._is_object_value,
        ]

        object_data = self._get_nested_dict_value(input_data, variable_path)

        for container_validator in object_container_validators:
            is_valid, error_msg = container_validator(object_data, variable_properties)
            if not is_valid:
                return self._handle_container_error(error_msg, variable_path, variable_properties, input_data)

        for key in object_data.keys():
            is_sub_element_acceptable = self._validate_input_type_dynamic(variable_properties[key],
                                                                          variable_path + [key], input_data)
            if not is_sub_element_acceptable:
                return False

        return True

    @staticmethod
    def _is_array_value(variable_value: Any, variable_properties: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check if the variable value is a list.

        Parameters
        ----------
        variable_value : Any
            The value of the variable to check.
        variable_properties : Dict[str, Any]
            The properties for the variable of interest.

        Returns
        -------
        Tuple[bool, str]
            A tuple containing a boolean indicating if the check passed and a string containing the reason for failure.
        """

        if type(variable_value) is not list:
            return False, "Array variable is not a list."
        return True, ""

    @staticmethod
    def _check_array_len_lower_bound(variable_value: List[Any],
                                     variable_properties: Dict[str, Any]) \
            -> Tuple[bool, str]:
        """
        Check if the list has a length greater than or equal to the minimum specified.

        Parameters
        ----------
        variable_value : List[Any]
            The value of the variable to check.
        variable_properties : Dict[str, Any]
            The properties for the variable of interest.

        Returns
        -------
        Tuple[bool, str]
            A tuple containing a boolean indicating if the check passed and a string containing the reason for failure.
        """

        if "minimum_length" in variable_properties and len(variable_value) < variable_properties["minimum_length"]:
            return False, f"Array length less than minimum: " \
                          f"{len(variable_value)} < {variable_properties['minimum_length']}"
        return True, ""

    @staticmethod
    def _check_array_len_upper_bound(variable_value: List[Any], variable_properties: Dict[str, Any]) \
            -> Tuple[bool, str]:
        """
        Check if the list has a length less than or equal to the maximum specified.

        Parameters
        ----------
        variable_value : List[Any]
            The value of the variable to check.
        variable_properties : Dict[str, Any]
            The properties for the variable of interest.

        Returns
        -------
        Tuple[bool, str]
            A tuple containing a boolean indicating if the check passed and a string containing the reason for failure.
        """

        if "maximum_length" in variable_properties and len(variable_value) > variable_properties["maximum_length"]:
            return False, f"Array length more than maximum: " \
                          f"{len(variable_value)} > {variable_properties['maximum_length']}"
        return True, ""

    def _validate_array_type(self, variable_path: List[str | int],
                             variable_properties: Dict[str, Any],
                             input_data: Dict[str, Any]) -> bool:
        """
        Validate an input data element of type array.

        Parameters
        ----------
        variable_path : List[str | int]
            The path to the variable by following the keys in the input_data dictionary.
        variable_properties : Dict[str, Any]
            The properties for the variable of interest.
        input_data : Dict[str, Any]
            A reference to the input data dictionary to enable in-place fixing.

        Returns
        -------
        bool
            True if the element was valid or fixed, False otherwise.
        """

        array_container_validators = [
            self._is_array_value,
            self._check_array_len_lower_bound,
            self._check_array_len_upper_bound,
        ]

        array_data = self._get_nested_dict_value(input_data, variable_path)

        for container_validator in array_container_validators:
            is_valid, error_msg = container_validator(array_data, variable_properties)
            if not is_valid:
                return self._handle_container_error(error_msg, variable_path, variable_properties, input_data)

        for idx in range(len(array_data)):
            is_sub_element_acceptable = self._validate_input_type_dynamic(variable_properties["properties"],
                                                                          variable_path + [idx],
                                                                          input_data)
            if not is_sub_element_acceptable:
                return False

        return True

    def _fix_data(self, variable_properties: Dict[str, Any],
                  variable_path: List[Union[str, int]],
                  input_data: Dict[str, Any]) -> bool:
        """
        Attempt to fix the invalid data.

        Parameters
        ----------
        variable_properties : dict[str, Any]
            The properties for the variable of interest.

        variable_path: list
            A list indicating the path to reach the variable of interest in self.__metadata and self.__pool.

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
            om.add_error("Validation: invalid data not able to be fixed: ", f"{variable_path[-1]}", info_map)
            return False
        variable_path_str = self._convert_variable_path_to_str(variable_path)
        variable_parent = self._get_nested_dict_value(input_data, variable_path[:-1])
        old_value = variable_parent[variable_path[-1]]
        variable_parent[variable_path[-1]] = variable_properties['default']
        om.add_warning("Data fixed",
                       f"{variable_path_str}: Replaced {old_value} with => {variable_properties['default']}",
                       info_map)

        # Remove the 'default' key to avoid potential recursive calls
        variable_properties.pop('default')

        return True

    def get_data(self, data_address: str) -> Any:
        """
        Get the requested data from the pool.

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
        The user can request as broad or narrow a selection of the input data pool as is needed.

        Input Manager must first be instantiated:
        >>> input_manager = InputManager()

        This will return the value of `calf_num` of the `herd_information` section in the `animal` blob
        (in this example, the value for `calf_num` is 8):
        >>> input_manager.get_data('animal.herd_information.calf_num')
        8

        If a broader range of data is needed, the user can expand the query to get_data
        by shortening the data_address. This will return the full herd_information object:
        >>> input_manager.get_data('animal.herd_information')
        {
        calf_num: 8,
        heiferI_num: 44,
        heiferII_num: 38,
        heiferIII_num_springers: 5,
        cow_num: 100,
        herd_num: 187,
        herd_init: False,
        breed: HO
        }
        """
        info_map = {"class": self.__class__.__name__,
                    "function": self.get_data.__name__,
                    }

        element_hierarchy = data_address.split('.')

        try:
            data_value = reduce(lambda d, key: d[key], element_hierarchy,
                                self.__pool)
            return deepcopy(data_value)

        except KeyError as key_error:
            invalid_key = str(key_error).strip("\'")
            parent_address = str(data_address.split("." + invalid_key)[0])

            om.add_error("Data not found:", f"Cannot find \"{data_address}\", "
                                            f"\"{parent_address}\" does not have attribute \"{invalid_key}\".",
                         info_map)

            raise KeyError(f"Data not found: Cannot find \"{data_address}\", "
                           f"\"{parent_address}\" does not have attribute \"{invalid_key}\".")

    def get_metadata(self, metadata_address: str) -> Any:
        """
        Get the requested metadata from the IM metadata dictionary.

        Parameters
        ----------
        metadata_address : str
            The address of the requested metadata.

        Returns
        -------
        Any
            The requested metadata if found.

        Raises
        -------
        KeyError
            If the requested metadata is not found.

        Examples
        -------
        The user can request as broad or narrow a selection of the metadata as is needed.

        Input Manager must first be instantiated:
        >>> input_manager = InputManager()

        This will return the 'type' for `albedo` in the `soil_profile_properties` section of the metadata's properties
        (the type for `albedo` is `number`):
        >>> input_manager.get_metadata('properties.soil_profile_properties.albedo.type')
        "number"

        If a broader range of the metadata is needed, the user can expand the query to get_metadata
        by shortening the metadata_address. This will return the full 'albedo' object containing its type,
        description, minimum, maximum, and default:
        >>> input_manager.get_metadata('properties.soil_profile_properties.albedo')
        {
        "type": "number",
        "description": "Ratio of solar radiation reflected by soil to amount of incident upon it.
        \nUnitless.\nReference: SWAT Input .SOL - SOL_ALB",
        "minimum": 0.0,
        "maximum": 1.0,
        "default": 0.16
        }
        """
        info_map = {"class": self.__class__.__name__,
                    "function": self.get_metadata.__name__,
                    }

        element_hierarchy = metadata_address.split('.')

        try:
            metadata_value = reduce(lambda d, key: d[key], element_hierarchy,
                                    self.__metadata)
            return deepcopy(metadata_value)

        except KeyError:
            invalid_key = element_hierarchy[-1]
            parent_address = ".".join(element_hierarchy[:-1])

            om.add_error("Data not found:", f"Cannot find \"{metadata_address}\", "
                                            f"\"{parent_address}\" does not have attribute \"{invalid_key}\".",
                         info_map)

            raise KeyError(f"Data not found: Cannot find \"{metadata_address}\", "
                           f"\"{parent_address}\" does not have attribute \"{invalid_key}\".")

    def flush_pool(self) -> None:
        """
        Clear the variable pool.
        """
        info_map = {"class": self.__class__.__name__,
                    "function": self.flush_pool.__name__,
                    }
        self.__pool = {}
        om.add_log("Clear variable pool", "The pool is emptied.", info_map)


class ElementsCounter:
    """
    A class to keep track of element counts in various categories: total, valid, fixed, and invalid.

    Attributes
    ----------
    total_elements : int
        The count of all elements processed.
    valid_elements : int
        The count of all valid elements processed.
    fixed_elements : int
        The count of all elements that were fixed during processing.
    invalid_elements : int
        The count of all elements found to be invalid during processing.

    Methods
    -------
    increment(name, value=1)
        Increment the count of a specific attribute by the given value.
    """

    def __init__(self):
        """
        Initialize the ElementsCounter with all counts set to zero.
        """

        self.total_elements = 0
        self.valid_elements = 0
        self.fixed_elements = 0
        self.invalid_elements = 0

    def update(self, name: str, value: int):
        """
        Update the count of a specific attribute by the given value.

        Parameters
        ----------
        name : str
            The name of the attribute to update.
        value : int
            The new value of the attribute.
        """

        if hasattr(self, name):
            setattr(self, name, value)
        else:
            raise Exception(f"Invalid counter name: {name}")

    def increment(self, name: str, value: int = 1):
        """
        Increment the count of a specific attribute by the given value.

        Parameters
        ----------
        name : str
            The name of the attribute to increment.
        value : int, optional
            The amount by which to increment the attribute (default is 1).

        Raises
        ------
        Exception
            If the given name is not an attribute of ElementsCounter.
        """

        self.update(name, getattr(self, name) + value)

    def decrement(self, name: str, value: int = 1):
        """
        Decrement the count of a specific attribute by the given value.

        Parameters
        ----------
        name : str
            The name of the attribute to decrement.
        value : int, optional
            The amount by which to decrement the attribute (default is 1).

        Raises
        ------
        Exception
            If the given name is not an attribute of ElementsCounter.
        """

        self.update(name, getattr(self, name) - value)

    def reset(self) -> None:
        """
        Reset all counts to zero.

        Returns
        -------
        None
        """

        self.total_elements = 0
        self.valid_elements = 0
        self.fixed_elements = 0
        self.invalid_elements = 0

    def __str__(self) -> str:
        """
        String representation of the ElementsCounter instance.

        Returns
        -------
        str
            A string representation of the ElementsCounter, showing the counts of all categories.
        """

        return str({
            "total_elements": self.total_elements,
            "valid_elements": self.valid_elements,
            "fixed_elements": self.fixed_elements,
            "invalid_elements": self.invalid_elements,
        })

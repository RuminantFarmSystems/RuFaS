# !/usr/bin/env python3
from __future__ import annotations

import json
import re
from copy import deepcopy
from functools import reduce
from typing import Any, Dict, List, Union

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
        self.counter = ElementCounter()

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
                    is_prop_valid = self._validate_json_element2(first_level_prop,
                                                                 properties_blob_key, input_data)
                elif file_type == "csv":
                    validation_result = self._validate_csv_element(first_level_prop, properties_blob_key, input_data,
                                                                   eager_termination)
                    is_prop_valid = validation_result["is_valid"]

                    for key, value in validation_result.items():
                        if key != "is_valid":
                            self.counter.increment(key, value)

                if is_prop_valid:
                    self.__pool[file_blob_key] = input_data
                elif eager_termination:
                    return False

        om.add_log("Total Valid Items", f"{self.counter.valid_elements}", info_map)
        om.add_log("Total Checked Items", f"{self.counter.total_elements}", info_map)
        om.add_log("Total Fixed Items", f"{self.counter.fixed_elements}", info_map)
        om.add_log("Total Invalid Items", f"{self.counter.invalid_elements}", info_map)

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
                                     prop_path: List[str | int],
                                     input_data_value: Any):
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
            "string": self._string_type_validator,
            "number": self._num_type_validator,
            "bool": self._bool_type_validator,
            "object": self._object_type_validator,
            "array": self._array_type_validator,
        }

        if var_type not in data_type_to_validator_map:
            raise KeyError(f"Invalid type {var_type}: Element must be type "
                           f"{list(data_type_to_validator_map.keys())}")

        return data_type_to_validator_map[var_type](variable_properties, prop_path, input_data_value)

    def _validate_csv_element(self, var_name: str, properties_blob_key: str, input_data: Dict[str, Any],
                              eager_termination: bool) -> dict:
        """
        Receives data loaded from csv input file and the validates each row element in the csv column it's sent.
        It attempts to fix any invalid elements and tracks the number of valid, invalid, fixed,
        and total elements from the input file are checked.

        Parameters
        ----------
        var_name : str
            The name of the csv data element being validated.
        properties_blob_key : str
            The metadata properties section keyword for the data input file being checked.
        input_data : Dict[str, Any]
            A buffer dictionary that holds the input data for validation and fixing.
        eager_termination : bool
            If true, the process will be terminated upon finding invalid data.

        Returns
        -------
        dict
            A dictionary that collects the counts of total elements checked,
            invalid elements, valid elements, and fixed elements as well as a boolean
            which is True if the data is valid, False otherwise.
        """
        info_map = {"class": self.__class__.__name__,
                    "function": self._validate_csv_element.__name__,
                    }
        element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                        "invalid_elements": 0, "is_valid": True}
        variable = input_data[var_name]
        variable_properties = reduce(lambda d, key: d[key], [var_name],
                                     self.__metadata["properties"][properties_blob_key])

        for element_num in range(len(variable)):
            element_counter_and_validity["total_elements"] += 1
            is_valid = self._validate_input_type_dynamic(variable_properties, var_name, variable[element_num])
            if is_valid:
                element_counter_and_validity["valid_elements"] += 1
            else:
                is_fixed = self._fix_data(variable_properties, [var_name, element_num], input_data)
                if is_fixed:
                    element_counter_and_validity["fixed_elements"] += 1
                else:
                    element_counter_and_validity["invalid_elements"] += 1
                    element_counter_and_validity["is_valid"] = False
                    om.add_warning("Invalid unfixable element found",
                                   f"{var_name} element {element_num} was invalid and could not be fixed", info_map)
                    if eager_termination:
                        return element_counter_and_validity

        return element_counter_and_validity

    def _validate_json_element(self, element_hierarchy: List[str], properties_blob_key: str,  # noqa
                               input_data: Dict[str, Any], eager_termination: bool, ) -> dict:
        """
        Receives data loaded from json input file, recursively finds and then validates nested elements,
        attempts to fix any invalid elements, and tracks the number of valid, invalid, fixed,
        and total elements from the input file are checked.

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
        dict
            A dictionary that collects the counts of total elements checked,
            invalid elements, valid elements, and fixed elements as well as a boolean
            which is True if the data is valid, False otherwise.


        """
        info_map = {"class": self.__class__.__name__,
                    "function": self._validate_json_element.__name__,
                    }
        element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                        "invalid_elements": 0, "is_valid": True}
        try:
            variable_properties = reduce(lambda d, key: d[key], element_hierarchy,
                                         self.__metadata["properties"][properties_blob_key])
        except KeyError as e:
            raise KeyError(f"{str(e)} not found in input data")

        if "type" not in variable_properties:
            raise KeyError("Missing 'type' key in variable_properties")
        is_nested = variable_properties["type"] == "object"
        if is_nested:
            children_status: Dict[str, bool] = {}
            false_counter = 0
            variable_properties_to_ignore = ["type", "description"]
            for nested_key in variable_properties.keys():
                if nested_key not in variable_properties_to_ignore:
                    element_hierarchy.append(nested_key)
                    element_counter_and_validity = self._validate_json_element(element_hierarchy, properties_blob_key,
                                                                               input_data, eager_termination)
                    is_child_valid = element_counter_and_validity["is_valid"]
                    if eager_termination and not is_child_valid:
                        return element_counter_and_validity
                    element_path = ".".join(element_hierarchy)
                    children_status[element_path] = is_child_valid
                    if not is_child_valid:
                        om.add_warning("Invalid nested element found", f"{element_path}", info_map)
                        false_counter += 1
                    element_hierarchy.remove(nested_key)

            is_valid = false_counter == 0
            element_counter_and_validity["is_valid"] = is_valid

            return element_counter_and_validity
        else:
            var_name = element_hierarchy[-1]

            try:
                input_data_value = reduce(lambda d, key: d[key], element_hierarchy, input_data)
            except KeyError:
                om.add_error("Key not found in input data", f"Key {var_name} not found in input data.", info_map)
                input_data_value = None

            is_valid = self._validate_input_type_dynamic(variable_properties, var_name, input_data_value)

            element_counter_and_validity["total_elements"] += 1
            if is_valid:
                element_counter_and_validity["valid_elements"] += 1
                return element_counter_and_validity
            else:
                is_fixed = self._fix_data(variable_properties, element_hierarchy, input_data)
                if is_fixed:
                    element_counter_and_validity["fixed_elements"] += 1
                else:
                    om.add_warning("Invalid unfixable element found",
                                   f"{var_name} was invalid and could not be fixed", info_map)
                    element_counter_and_validity["invalid_elements"] += 1
                    element_counter_and_validity["is_valid"] = False
                return element_counter_and_validity

    def _validate_json_element2(self,
                                first_level_prop: str,
                                properties_blob_key: str,
                                input_data: dict[str, Any]
                                ) -> bool:
        variable_properties = self._get_nested_dict_value(
            self.__metadata["properties"][properties_blob_key], [first_level_prop]
        )

        return self._validate_input_type_dynamic(variable_properties,
                                                 [first_level_prop],
                                                 input_data)

    @staticmethod
    def _get_nested_dict_value(data, keys: list[str | int]):
        for key in keys:
            if type(data) in (list, dict):
                data = data[key]
            else:
                return data
        return data

    def _num_type_validator(self, variable_properties: Dict[str, Any],
                            prop_path: List[str | int],
                            input_data) -> bool:
        """Validates an input data number element."""
        self.counter.increment("total_elements")

        info_map = {"class": self.__class__.__name__,
                    "function": self._num_type_validator.__name__,
                    }
        minimum_value = variable_properties.get("minimum")
        maximum_value = variable_properties.get("maximum")

        element_to_validate = self._get_nested_dict_value(input_data, prop_path)

        if not type(element_to_validate) in (int, float):
            om.add_warning("Value is not a number.", f"{prop_path[-1]=}", info_map)

            if self._fix_data(variable_properties, prop_path, input_data):
                self.counter.increment("fixed_elements")
                return True

            self.counter.increment("invalid_elements")
            return False

        if minimum_value is not None:
            is_in_range = minimum_value <= element_to_validate
            if not is_in_range:
                om.add_warning("Value less than minimum.", f"{prop_path[-1]=}", info_map)

                if self._fix_data(variable_properties, prop_path, input_data):
                    self.counter.increment("fixed_elements")
                    return True

        if maximum_value is not None:
            is_in_range = element_to_validate <= maximum_value
            if not is_in_range:
                om.add_warning("Value greater than maximum.", f"{prop_path[-1]=}", info_map)

                if self._fix_data(variable_properties, prop_path, input_data):
                    self.counter.increment("fixed_elements")
                    return True

                self.counter.increment("invalid_elements")
                return False

        self.counter.increment("valid_elements")
        return True

    def _string_type_validator(self, variable_properties: Dict[str, Any],
                               prop_path: List[str | int],
                               input_data: Dict[str, Any]) -> bool:
        """Validates an input data string element."""
        self.counter.increment("total_elements")

        info_map = {"class": self.__class__.__name__,
                    "function": self._string_type_validator.__name__,
                    }

        element_to_validate = self._get_nested_dict_value(input_data, prop_path)
        if type(element_to_validate) is not str:
            om.add_warning("String variable is not a string.", f"{prop_path[-1]=}", info_map)

            if self._fix_data(variable_properties, prop_path, input_data):
                self.counter.increment("fixed_elements")
                return True

            self.counter.increment("invalid_elements")
            return False

        pattern_check = variable_properties.get("pattern")
        if pattern_check is not None:
            is_valid_string = bool(re.match(pattern_check, element_to_validate))
            if not is_valid_string:
                om.add_warning("String variable must match pattern.", f"{prop_path[-1]=}", info_map)
                if self._fix_data(variable_properties, prop_path, input_data):
                    self.counter.increment("fixed_elements")
                    return True

                self.counter.increment("invalid_elements")
                return False

        minimum_length = variable_properties.get("minimum_length")
        maximum_length = variable_properties.get("maximum_length")
        if minimum_length is not None:
            is_valid_string = variable_properties["minimum_length"] <= len(element_to_validate)
            if not is_valid_string:
                om.add_warning("String length less than minimum.", f"{prop_path[-1]=}", info_map)

                if self._fix_data(variable_properties, prop_path, input_data):
                    self.counter.increment("fixed_elements")
                    return True

                self.counter.increment("invalid_elements")
                return False

        if maximum_length is not None:
            is_valid_string = len(element_to_validate) <= variable_properties["maximum_length"]
            if not is_valid_string:
                om.add_warning("String length more than maximum.", f"{prop_path[-1]=}", info_map)

                if self._fix_data(variable_properties, prop_path, input_data):
                    self.counter.increment("fixed_elements")
                    return True

                self.counter.increment("invalid_elements")
                return False

        self.counter.increment("valid_elements")
        return True

    def _bool_type_validator(self, variable_properties: Dict[str, Any],
                             prop_path: List[str | int], input_data: Dict[str, Any]) -> bool:
        """Validates an input data bool element."""
        self.counter.increment("total_elements")

        element_to_validate = self._get_nested_dict_value(input_data, prop_path)
        if type(element_to_validate) is bool:
            self.counter.increment("valid_elements")
            return True

        if self._fix_data(variable_properties, prop_path, input_data):
            self.counter.increment("fixed_elements")
            return True

        self.counter.increment("invalid_elements")
        return False

    def _object_type_validator(self, variable_properties: Dict[str, Any],
                               prop_path: List[str | int],
                               input_data: Dict[str, Any]) -> bool:
        """Validates an input data object element."""
        element_to_validate = self._get_nested_dict_value(input_data, prop_path)

        if type(element_to_validate) is not dict:
            self.counter.increment("total_elements")
            self.counter.increment("invalid_elements")
            return False

        for key in element_to_validate.keys():
            if key not in variable_properties:
                self.counter.increment("total_elements")
                self.counter.increment("invalid_elements")
                return False
            is_valid = self._validate_input_type_dynamic(variable_properties[key], prop_path + [key], input_data)
            if not is_valid:
                return False

        return True

    def _array_type_validator(self, variable_properties: Dict[str, Any],
                              prop_path: List[str | int],
                              input_data: list) -> bool:
        """Validates an input data element of type array."""
        info_map = {"class": self.__class__.__name__,
                    "function": self._array_type_validator.__name__,
                    }
        element_to_validate = self._get_nested_dict_value(input_data, prop_path)
        if type(element_to_validate) is not list:
            om.add_warning("Array is not a list.", f"{prop_path[-1]=}", info_map)

            self.counter.increment("total_elements")
            self.counter.increment("invalid_elements")
            return False

        maximum_length = variable_properties.get("maximum_length")
        minimum_length = variable_properties.get("minimum_length")
        if minimum_length is not None:
            is_in_range = variable_properties["minimum_length"] <= len(element_to_validate)
            if not is_in_range:
                om.add_warning("Array length less than minimum.", f"{prop_path[-1]=}", info_map)
                self.counter.increment("total_elements")
                self.counter.increment("invalid_elements")
                return False

        if maximum_length is not None:
            is_in_range = len(element_to_validate) <= variable_properties["maximum_length"]
            if not is_in_range:
                om.add_warning("Array length more than maximum.", f"{prop_path[-1]=}", info_map)
                self.counter.increment("total_elements")
                self.counter.increment("invalid_elements")
                return False

        for idx in range(len(element_to_validate)):
            is_valid = self._validate_input_type_dynamic(variable_properties["properties"],
                                                         prop_path + [idx],
                                                         input_data)
            if not is_valid:
                return False

        return True

    def _fix_data(self, variable_properties: Dict[str, Any],
                  element_hierarchy: List[Union[str, int]],
                  input_data: Dict[str, Any]) -> bool:
        """
        Attempt to fix the invalid data.

        Parameters
        ----------
        variable_properties : dict[str, Any]
            The properties for the variable of interest.

        element_hierarchy: list
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
            return False
        variable_parent = self._get_nested_dict_value(input_data, element_hierarchy[:-1])
        variable_parent[element_hierarchy[-1]] = variable_properties['default']
        om.add_warning("Data fixed",
                       f"Invalid data fixed: {element_hierarchy[-1]} => {variable_properties['default']}",
                       info_map)
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


class ElementCounter:
    def __init__(self):
        self.total_elements = 0
        self.valid_elements = 0
        self.fixed_elements = 0
        self.invalid_elements = 0

    def update(self, name: str, value: int):
        if hasattr(self, name):
            setattr(self, name, value)
        else:
            raise Exception(f"Invalid counter name: {name}")

    def increment(self, name: str, value: int = 1):
        self.update(name, getattr(self, name) + value)

    def decrement(self, name: str, value: int = 1):
        self.update(name, getattr(self, name) - value)

    def merge(self, other: ElementCounter):
        for key in vars(self):
            setattr(self, key, getattr(self, key) + getattr(other, key))

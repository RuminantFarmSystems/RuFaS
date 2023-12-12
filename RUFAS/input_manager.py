# !/usr/bin/env python3

from copy import deepcopy
from functools import reduce
import json
import re

import pandas as pd
from RUFAS.output_manager import OutputManager
from typing import Any, Dict, List, Union, Callable

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
        valid_elements_counter = 0
        invalid_elements_counter = 0
        total_elements_counter = 0
        fixed_elements_counter = 0

        data_type_to_loader_map: Dict[str, Callable] = {"json": self._load_data_from_json,
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
            metadata_properties = self.__metadata["properties"][properties_blob_key]
            filtered_input_data = self._filter_input_data_by_metadata(input_data, metadata_properties)
            for metadata_property in metadata_properties.keys():
                element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                                "invalid_elements": 0, "is_valid": True}
                if file_type == "json":
                    element_counter_and_validity = self._validate_dict_element([metadata_property], properties_blob_key,
                                                                               filtered_input_data, eager_termination,
                                                                               element_counter_and_validity)
                if file_type == "csv":
                    element_counter_and_validity = self._validate_tabular_element(metadata_property,
                                                                                  properties_blob_key,
                                                                                  filtered_input_data,
                                                                                  eager_termination,
                                                                                  element_counter_and_validity)

                fixed_elements_counter += element_counter_and_validity["fixed_elements"]
                valid_elements_counter += element_counter_and_validity["valid_elements"]
                total_elements_counter += element_counter_and_validity["total_elements"]
                if element_counter_and_validity["is_valid"]:
                    self.__pool[file_blob_key] = filtered_input_data
                else:
                    if not eager_termination:
                        invalid_elements_counter += element_counter_and_validity["invalid_elements"]
                    else:
                        return False

        om.add_log("Validation count: total items", f"{total_elements_counter=}", info_map)
        om.add_log("Validation count: total valid", f"{valid_elements_counter=}", info_map)
        om.add_log("Validation count: total fixed", f"{fixed_elements_counter=}", info_map)
        om.add_log("Validation count: total invalid", f"{invalid_elements_counter=}", info_map)
        return invalid_elements_counter == 0

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

    def _validate_input_type_dynamic(self, variable_properties: Dict[str, Any], var_name: str, input_data_value: Any,
                                     properties_blob_key: str) -> bool:
        """
        Validates the input data value based on its specified dynamic type.

        Parameters
        ----------
        variable_properties : Dict[str, Any]
            A dictionary containing properties relevant to the validation.

        var_name : str
            The name of the variable being validated.

        input_data_value : Any
            The input data value to be validated.

        properties_blob_key : str
            The metadata properties section keyword for the data input file being checked.

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
            raise KeyError("Missing 'type' key in variable_properties")
        var_type = variable_properties["type"]
        data_type_to_validator_map = {
            "string": self._string_type_validator,
            "number": self._num_type_validator,
            "array": self._array_type_validator,
            "bool": self._bool_type_validator,
        }
        try:
            validator = data_type_to_validator_map[var_type]
        except KeyError:
            raise KeyError(
                f"Invalid type {var_type}: Element must be type {data_type_to_validator_map.keys()}"
            )
        return validator(variable_properties, var_name, input_data_value, properties_blob_key)

    def _validate_tabular_element(self, var_name: str, properties_blob_key: str, input_data: Dict[str, Any],
                                  eager_termination: bool, element_counter_and_validity: Dict[str, int | bool]
                                  ) -> Dict[str, int | bool]:
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

        element_counter_and_validity : Dict[str, int | bool]
            A dictionary that collects the counts of total elements checked,
            invalid elements, valid elements, and fixed elements as well as a boolean
            which is True if the data is valid, False otherwise.

        Returns
        -------
        dict
            A dictionary that collects the counts of total elements checked,
            invalid elements, valid elements, and fixed elements as well as a boolean
            which is True if the data is valid, False otherwise.
        """
        info_map = {"class": self.__class__.__name__,
                    "function": self._validate_tabular_element.__name__,
                    }
        variable = input_data[var_name]
        variable_properties = reduce(lambda d, key: d[key], [var_name],
                                     self.__metadata["properties"][properties_blob_key])

        for element_num in range(len(variable)):
            element_counter_and_validity["total_elements"] += 1
            is_valid = self._validate_input_type_dynamic(variable_properties, var_name, variable[element_num],
                                                         properties_blob_key)
            if is_valid:
                element_counter_and_validity["valid_elements"] += 1
            else:
                is_fixed = self._fix_data(variable_properties, [var_name, element_num], input_data, properties_blob_key)
                if is_fixed:
                    element_counter_and_validity["fixed_elements"] += 1
                else:
                    element_counter_and_validity["invalid_elements"] += 1
                    element_counter_and_validity["is_valid"] = False
                    om.add_warning("Validation: invalid unfixable element found",
                                   f"{var_name} element {element_num} was invalid and could not be fixed", info_map)
                    if eager_termination:
                        return element_counter_and_validity

        return element_counter_and_validity

    def _validate_dict_element(self, element_hierarchy: List[str], properties_blob_key: str,  # noqa
                               input_data: Dict[str, Any], eager_termination: bool,
                               element_counter_and_validity: Dict[str, int | bool], ) -> dict:
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

        element_counter_and_validity : Dict[str, int | bool]
            A dictionary that collects the counts of total elements checked,
            invalid elements, valid elements, and fixed elements as well as a boolean
            which is True if the data is valid, False otherwise.

        Returns
        -------
        dict
            A dictionary that collects the counts of total elements checked,
            invalid elements, valid elements, and fixed elements as well as a boolean
            which is True if the data is valid, False otherwise.


        """
        info_map = {"class": self.__class__.__name__,
                    "function": self._validate_dict_element.__name__,
                    }
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
                    element_counter_and_validity = self._validate_dict_element(element_hierarchy, properties_blob_key,
                                                                               input_data, eager_termination,
                                                                               element_counter_and_validity)
                    is_child_valid = element_counter_and_validity["is_valid"]
                    if eager_termination and not is_child_valid:
                        return element_counter_and_validity
                    element_path = ".".join(element_hierarchy)
                    children_status[element_path] = is_child_valid
                    if not is_child_valid:
                        om.add_warning("Validation: invalid nested element found", f"{element_path}", info_map)
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
                om.add_error("Validation: key not found in input data", f"Key {var_name} not found in input data.",
                             info_map)
                input_data_value = None

            is_valid = self._validate_input_type_dynamic(variable_properties, var_name, input_data_value,
                                                         properties_blob_key)

            element_counter_and_validity["total_elements"] += 1
            if is_valid:
                element_counter_and_validity["valid_elements"] += 1
                return element_counter_and_validity
            else:
                is_fixed = self._fix_data(variable_properties, element_hierarchy, input_data, properties_blob_key)
                if is_fixed:
                    element_counter_and_validity["fixed_elements"] += 1
                else:
                    om.add_warning("Validation: invalid unfixable element found",
                                   f"Variable: '{var_name}' was invalid and could not be fixed", info_map)
                    element_counter_and_validity["invalid_elements"] += 1
                    element_counter_and_validity["is_valid"] = False
                return element_counter_and_validity

    def _array_type_validator(self, variable_properties: Dict[str, Any], var_name: str, input_data_value: list,
                              properties_blob_key: str) -> bool:
        """Validates an input data element of type array."""
        info_map = {"class": self.__class__.__name__,
                    "function": self._array_type_validator.__name__,
                    }
        properties_violation_message = f"Violates properties defined in metadata properties section" \
                                       f" '{properties_blob_key}'."
        if type(input_data_value) is not list:
            warning_string = "Validation: array is not a list"
            warning_message = f"Variable: '{var_name}' is type: {type(input_data_value)}. " \
                              f"{properties_violation_message}"
            om.add_warning(warning_string, warning_message, info_map)
            return False

        maximum_length = variable_properties.get("maximum_length")
        minimum_length = variable_properties.get("minimum_length")
        if minimum_length is not None:
            is_in_range = variable_properties["minimum_length"] <= len(input_data_value)
            if not is_in_range:
                warning_name = "Validation: array length less than minimum"
                warning_message = f"Variable: '{var_name}' has length: {len(input_data_value)}, less than minimum " \
                                  f"length: {minimum_length}. {properties_violation_message}"
                om.add_warning(warning_name, warning_message, info_map)
                return False
        if maximum_length is not None:
            is_in_range = len(input_data_value) <= variable_properties["maximum_length"]
            if not is_in_range:
                warning_name = "Validation: array length greater than maximum"
                warning_message = f"Variable: '{var_name}' has length: {len(input_data_value)}, greater than " \
                                  f"maximum length: {maximum_length}. {properties_violation_message}"
                om.add_warning(warning_name, warning_message, info_map)
                return False
        return True

    def _num_type_validator(self, variable_properties: Dict[str, Any], var_name: str,
                            input_data_value: Union[int, float], properties_blob_key: str) -> bool:
        """Validates an input data number element."""
        info_map = {"class": self.__class__.__name__,
                    "function": self._num_type_validator.__name__,
                    }
        minimum_value = variable_properties.get("minimum")
        maximum_value = variable_properties.get("maximum")
        properties_violation_message = f"Violates properties defined in metadata properties section" \
                                       f" '{properties_blob_key}'."
        if type(input_data_value) is not float and type(input_data_value) is not int:
            warning_string = "Validation: value is not a number"
            warning_message = f"Variable: '{var_name}' has value: {input_data_value}, is type: " \
                              f"{type(input_data_value)}. {properties_violation_message}"
            om.add_warning(warning_string, warning_message, info_map)
            return False
        if minimum_value is not None:
            is_in_range = minimum_value <= input_data_value
            if not is_in_range:
                warning_name = "Validation: value less than minimum"
                warning_message = f"Variable: '{var_name}' has value: {input_data_value}, less than minimum value: " \
                                  f"{minimum_value: .2f}. {properties_violation_message}"
                om.add_warning(warning_name, warning_message, info_map)
                return False
        if maximum_value is not None:
            is_in_range = input_data_value <= maximum_value
            if not is_in_range:
                warning_name = "Validation: value greater than maximum"
                warning_string = f"Variable: '{var_name}' has value: {input_data_value}, greater than maximum value: " \
                                 f"{maximum_value: .2f}. {properties_violation_message}"
                om.add_warning(warning_name, warning_string, info_map)
                return False

        return True

    def _string_type_validator(self, variable_properties: Dict[str, Any], var_name: str, input_data_value: str,
                               properties_blob_key: str) -> bool:
        """Validates an input data string element."""
        info_map = {"class": self.__class__.__name__,
                    "function": self._string_type_validator.__name__,
                    }
        properties_violation_message = f"Violates properties defined in metadata properties section" \
                                       f" '{properties_blob_key}'."
        if type(input_data_value) is not str:
            warning_name = "Validation: string variable is not a string"
            warning_message = f"Variable: '{var_name}' has value: {input_data_value}, is type: " \
                              f"{type(input_data_value)}. {properties_violation_message}"
            om.add_warning(warning_name, warning_message, info_map)
            return False

        pattern_check = variable_properties.get("pattern")
        if pattern_check is not None:
            is_valid_string = bool(re.match(pattern_check, input_data_value))
            if not is_valid_string:
                warning_name = "Validation: string variable does not match pattern"
                warning_message = f"Variable: '{var_name}' has value: '{input_data_value}', does not match pattern: " \
                                  f"{pattern_check}. {properties_violation_message}"
                om.add_warning(warning_name, warning_message, info_map)
                return False

        minimum_length = variable_properties.get("minimum_length")
        maximum_length = variable_properties.get("maximum_length")
        if minimum_length is not None:
            is_valid_string = variable_properties["minimum_length"] <= len(input_data_value)
            if not is_valid_string:
                warning_name = "Validation: string length less than minimum"
                warning_message = f"Variable: '{var_name}' has value: '{input_data_value}', length is less than " \
                                  f"minimum length: {minimum_length}. {properties_violation_message}"
                om.add_warning(warning_name, warning_message, info_map)
                return False
        if maximum_length is not None:
            is_valid_string = len(input_data_value) <= variable_properties["maximum_length"]
            if not is_valid_string:
                warning_name = "Validation: string length greater than maximum"
                warning_message = f"Variable: '{var_name}' has value: '{input_data_value}', length is greater than " \
                                  f"maximum length: {maximum_length}. {properties_violation_message}"
                om.add_warning(warning_name, warning_message, info_map)
                return False

        return True

    def _bool_type_validator(self, variable_properties: Dict[str, Any], var_name: str, input_data_value: bool,
                             properties_blob_key: str) -> bool:
        """Validates an input data bool element."""
        info_map = {"class": self.__class__.__name__,
                    "function": self._bool_type_validator.__name__,
                    }
        properties_violation_message = f"Violates properties defined in metadata properties section" \
                                       f" '{properties_blob_key}'."
        if type(input_data_value) is not bool:
            warning_name = "Validation: bool variable is not a bool"
            warning_message = f"Variable: '{var_name}' has value: '{input_data_value}', is type: " \
                              f"'{type(input_data_value)}'. {properties_violation_message}"
            om.add_warning(warning_name, warning_message, info_map)
            return False

        return input_data_value in (True, False)

    def _fix_data(self, variable_properties: Dict[str, Any], element_hierarchy: List[Union[str, int]],
                  input_data: Dict[str, Any], properties_blob_key: str) -> bool:
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

        properties_blob_key : str
            The metadata properties section keyword for the data input file being checked.

        Returns
        -------
        bool
            True if the data is fixed, False otherwise.
        """
        info_map = {"class": self.__class__.__name__,
                    "function": self._fix_data.__name__,
                    }

        variable_parent = reduce(lambda d, key: d[key], element_hierarchy[:-1],
                                 input_data)

        element_path = ".".join([str(element) for element in element_hierarchy])
        properties_violation_message = f"Violates properties defined in metadata properties section" \
                                       f" '{properties_blob_key}'."
        if 'default' not in variable_properties.keys():
            error_message = f"Variable: '{element_path}' has invalid value: {variable_parent[element_hierarchy[-1]]}" \
                            f", and cannot be changed to a default value. {properties_violation_message}"
            om.add_error("Validation: invalid data not able to be fixed", error_message, info_map)
            return False

        original_invalid_value = variable_parent[element_hierarchy[-1]]
        warning_message = f"Variable: '{element_path}' has value: {original_invalid_value}. " \
                          f"{properties_violation_message}"
        om.add_warning("Validation: invalid data found",
                       warning_message,
                       info_map)

        variable_parent[element_hierarchy[-1]] = variable_properties['default']

        warning_message = f"Invalid data fixed: '{element_path}' value changed from {original_invalid_value} to " \
                          f"{variable_properties['default']}. Fix enabled by default value specified in " \
                          f"'{properties_blob_key}'."
        om.add_warning("Validation: data fixed", warning_message, info_map)
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

            om.add_error("Validation: data not found:", f"Cannot find \"{data_address}\", "
                                                        f"\"{parent_address}\" does not have attribute "
                                                        f"\"{invalid_key}\".",
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

            om.add_error("Validation: data not found:", f"Cannot find \"{metadata_address}\", "
                                                        f"\"{parent_address}\" does not have attribute "
                                                        f"\"{invalid_key}\".",
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

    def _metadata_properties_exists(self, variable_name: str, properties_blob_key: str) -> (bool,
                                                                                            KeyError | ValueError |
                                                                                            None):
        """
        Checks if specific properties exist in the metadata for a given variable.

        Notes
        -----
        This function is designed to verify the existence of specified properties
        within the metadata of a particular variable. It returns a boolean indicating
        the existence of the properties, and a KeyError in case of missing metadata
        or properties.

        Parameters
        ----------
        variable_name : str
            The name of the variable for which the metadata is to be checked.
        properties_blob_key : str
            The key representing the specific properties blob in the metadata to check.

        Returns
        -------
        tuple
            A tuple containing a boolean and an exception:
            - The boolean is True if the properties exist, False otherwise.
            - KeyError if the metadata is not loaded or the properties are not found,
              otherwise None.
            """
        info_map = {"class": self.__class__.__name__,
                    "function": self._metadata_properties_exists.__name__,
                    }
        if not self.__metadata:
            om.add_error("No metadata loaded", "No metadata is loaded to the InputManager.", info_map)
            return False, ValueError("No metadata loaded.")
        if properties_blob_key not in self.__metadata["properties"]:
            om.add_error("No metadata found", f"No metadata is found for variable '{variable_name}' with given "
                                              f"properties_blob_key {properties_blob_key}.", info_map)
            return False, KeyError(f"No metadata is found for variable '{variable_name}' with given properties_blob_key"
                                   f" {properties_blob_key}.")
        return True, None

    def _add_variable_to_pool(self, variable_name: str, data: Dict[str, Any], properties_blob_key: str,
                              eager_termination: bool, is_dict_variable: bool) -> (bool, ValueError | None):
        """
        Adds a variable to the pool after validating its data against specified metadata properties.

        Notes
        -----
        This function processes and validates the input data for a variable based on
        its metadata properties. It then adds the validated data to a pool. The function
        also provides an option for eager termination in case of invalid data.

        Parameters
        ----------
        variable_name : str
            The name of the variable to be added to the pool.
        data : Dict[str, Any]
            The data associated with the variable that needs validation and addition to the pool.
        properties_blob_key : str
            The key in the metadata properties against which the data is validated.
        eager_termination : bool
            Flag indicating whether the function should return early in case of invalid data.
        is_dict_variable : bool
            Weather the variable is a dictionary variable (rather than tabular).

        Returns
        -------
        tuple
            A tuple containing a boolean and an exception:
            - The boolean is True if the variable is successfully added, False otherwise.
            - ValueError if invalid data is encountered and eager_termination is True,
              otherwise None.

        """
        info_map = {"class": self.__class__.__name__,
                    "function": self._add_variable_to_pool.__name__,
                    }
        element_counter = {"valid_elements": 0, "invalid_elements": 0,
                           "total_elements": 0, "fixed_elements": 0}
        validated_data = {}

        metadata_properties = self.__metadata["properties"][properties_blob_key]
        for metadata_property in metadata_properties.keys():
            element_counter_and_validity = {
                "fixed_elements": 0, "total_elements": 0, "valid_elements": 0, "invalid_elements": 0,
                "is_valid": True}
            if is_dict_variable:
                element_counter_and_validity = self._validate_dict_element(
                    element_hierarchy=[metadata_property],
                    properties_blob_key=properties_blob_key,
                    input_data=data,
                    eager_termination=eager_termination,
                    element_counter_and_validity=element_counter_and_validity
                )
            else:
                element_counter_and_validity = self._validate_tabular_element(
                    var_name=metadata_property,
                    properties_blob_key=properties_blob_key,
                    input_data=data,
                    eager_termination=eager_termination,
                    element_counter_and_validity=element_counter_and_validity
                )

            for key in element_counter.keys():
                element_counter[key] += element_counter_and_validity[key]

            if element_counter_and_validity["is_valid"]:
                validated_data[metadata_property] = data[metadata_property]

        om.add_log(f"Validation count for variable {variable_name}: total items",
                   f"{element_counter['total_elements']=}", info_map)
        om.add_log(f"Validation count for variable {variable_name}: total valid",
                   f"{element_counter['valid_elements']=}", info_map)
        om.add_log(f"Validation count for variable {variable_name}: total fixed",
                   f"{element_counter['fixed_elements']=}", info_map)
        om.add_log(f"Validation count for variable {variable_name}: total invalid",
                   f"{element_counter['invalid_elements']=}", info_map)

        if variable_name in self.__pool.keys():
            om.add_warning("Overwriting existing variable", f"Variable {variable_name} already exists in InputManager "
                                                            f"pool, overwriting the old value.", info_map)

        self.__pool[variable_name] = validated_data

        if element_counter['invalid_elements'] > 0:
            om.add_error("Invalid variable",
                         f"Variable {variable_name} has invalid components. Only successfully validated components are "
                         f"added to InputManager pool during runtime.",
                         info_map)
            if eager_termination:
                return False, ValueError(
                    f"Variable {variable_name} has invalid components. Only successfully validated components are added"
                    f" to InputManager pool during runtime.")
            else:
                return False, None
        else:
            return True, None

    def add_dict_variable_to_pool(self, variable_name: str, data: Dict[str, Any], properties_blob_key: str,
                                  eager_termination: bool) -> bool:
        """
        Adds a dictionary variable to the InputManager's pool after validating it against metadata.

        This function takes in a variable along with its name and a key to access its validation metadata.
        It validates the data against the provided metadata and adds the data to the InputManager pool if it is valid.

        Parameters
        ----------
        variable_name: str
            The name of the dictionary variable to be added.
        data : Dict[str, Any]
            The data of the variable, structured as a dictionary.
        properties_blob_key : str
            A key used to locate the metadata for validation of the variable.
        eager_termination : bool
            If True, raises a RuntimeError when the variable is invalid.
            If False, the function returns False without raising an error.

        Returns
        -------
        bool
            True if the variable is successfully validated and added to the pool.
            False if the variable is invalid and not added to the pool.

        Raises
        -------
        TypeError
            If `data` is not the expected type of Dict[str, Any].
        KeyError
            If no metadata is loaded in InputManager.__metadata; or if no metadata property can be found with the given
            `properties_blob_key`.
        ValueError
            If eager_termination is True and the variable failed validation.
        """
        info_map = {"class": self.__class__.__name__,
                    "function": self.add_dict_variable_to_pool.__name__,
                    }
        if not (isinstance(data, Dict)):
            om.add_error("Incorrect variable type", f"Variable {variable_name} has type {type(data)}, does not match "
                                                    f"the expected type of `Dict[str, Any]`.",
                         info_map)
            raise TypeError("Incorrect variable type. Expected types: `data: Dict[str, Any]`.")

        metadata_properties_exists, metadata_error = self._metadata_properties_exists(
            variable_name=variable_name,
            properties_blob_key=properties_blob_key)

        if not metadata_properties_exists:
            raise metadata_error

        add_variable_success, add_variable_value_error = self._add_variable_to_pool(
            variable_name=variable_name,
            data=data,
            properties_blob_key=properties_blob_key,
            eager_termination=eager_termination,
            variable_type='dict')

        if not add_variable_success and add_variable_value_error:
            raise add_variable_value_error

        return add_variable_success

    def add_tabular_variable_to_pool(self, variable_name: str, data: Dict[str, List[Any]] | List[Any],
                                     properties_blob_key: str, eager_termination: bool) -> bool:
        """
        Adds a tabular variable to the InputManager's pool after validating it against metadata.

        This function takes in a variable along with its name and a key to access its validation metadata.
        It validates the data against the provided metadata and adds the data to the InputManager pool if it is valid.

        Parameters
        ----------
        variable_name: str
            The name of the variable to be added.
        data : Dict[str, List[Any]] | List[Any]
            The data of the tabular variable, structured as a dictionary of lists or a list.
        properties_blob_key : str
            A key used to locate the metadata for validation of the variable.
        eager_termination : bool
            If True, raises a ValueError when the variable is invalid.
            If False, the function returns False without raising an error.

        Returns
        -------
        bool
            True if the variable is successfully validated and added to the pool.
            False if the variable is invalid and not added to the pool.

        Raises
        -------
        TypeError
            If `data` is not the expected type of Dict[str, List[Any]] | List[Any].
        KeyError
            If no metadata is loaded in InputManager.__metadata; or if no metadata property can be found with the given
            `properties_blob_key`.
        ValueError
            If eager_termination is True and the variable failed validation.
        """
        info_map = {"class": self.__class__.__name__,
                    "function": self.add_tabular_variable_to_pool.__name__,
                    }
        if not (isinstance(data, Dict) or isinstance(data, List)):
            om.add_error("Incorrect variable type", f"Variable {variable_name} has type {type(data)}, does not match "
                                                    f"the expected type of `Dict[str, List[Any]] | List[Any]`.",
                         info_map)
            raise TypeError("Incorrect variable type. Expected types: `data: Dict[str, List[Any]] | List[Any]`.")

        data = {variable_name: data} if isinstance(data, List) else data

        metadata_properties_exists, metadata_error = self._metadata_properties_exists(
            variable_name=variable_name,
            properties_blob_key=properties_blob_key)

        if not metadata_properties_exists:
            raise metadata_error

        add_variable_success, add_variable_value_error = self._add_variable_to_pool(
            variable_name=variable_name,
            data=data,
            properties_blob_key=properties_blob_key,
            eager_termination=eager_termination,
            variable_type='tabular')

        if not add_variable_success and add_variable_value_error:
            raise add_variable_value_error

        return add_variable_success

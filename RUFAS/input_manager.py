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
        invalid_elements_counter = 0
        fixed_elements_counter = 0
        invalid_critical_elements_counter = 0
        total_elements_checked_counter = 0

        for module_key in self.__pool.keys():
            files_details = self.__metadata["files"]
            property_map_key = files_details[module_key]["properties"]
            module_properties = self.__metadata["properties"][property_map_key]
            for element in module_properties.keys():
                total_elements_checked_counter += 1
                is_valid = self._validate_element(module_key, element, property_map_key)
                if is_valid:
                    valid_elements_counter += 1
                else:
                    invalid_elements_counter += 1
                    is_data_fixed = self._fix_data(element, property_map_key)
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

    def _validate_element(self, module_key: str, element: str,
                          property_map_key: str, eager_termination: bool = True) -> bool:
        """
        Perform data validation checks.

        Parameters
        ----------
        element : str
            The key of the data to validate.

        property_map_kay : str
            The metadata properties section for the data input file being checked.

        eager_termination : bool, default=True
            If true, the process will be terminated upon finding invalid data.

        Returns
        -------
        bool
            True if the data is valid, False otherwise.
        """
        element_heirarchy = element.split(".")
        variable_to_check = reduce(lambda d, key: d[key], element_heirarchy,
                                   self.__metadata["properties"][property_map_key])
        non_nested_types = ["number", "string", "boolean", "array"]
        if variable_to_check["type"] in non_nested_types:
            is_nested = False
        elif variable_to_check["type"] == "object":
            is_nested = True
        else:
            # assume if no type then is object and make is_nested False?
            is_nested = False
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
                    false_counter += 1
            is_valid = false_counter == 0
            if is_valid:
                return True
            else:
                # TODO logging
                return False
        else:
            var_type = variable_to_check["type"]
            if var_type == "string":
                is_valid = self._validate_string_type_element(module_key, element_heirarchy, variable_to_check)
            elif var_type == "number":
                is_valid = self._validate_number_type_element(module_key, element_heirarchy, variable_to_check)
            elif var_type == "boolean":
                is_valid = self._validate_bool_type_element(module_key, element_heirarchy, variable_to_check)
            else:
                is_valid = self._validate_array_type_element(module_key, element_heirarchy, variable_to_check)

            if is_valid:
                return True
            else:
                is_fixed = self._fix_data()
                return is_fixed

    def _get_value_from_pool(self, module_key: str, element_heirarchy: List[str]) -> Any:
        """
        Convert and then use string path to get value for variable being checked.

        Parameters
        ----------
        element_heirarchy : str
            The nested element heirarchy of the data being checked.

        property_map_kay : str
            The metadata properties section for the data input file being checked.

        Returns
        -------
        result : Dict[str, Any]
            The nested metadata structure found by the path.
        """
        result = reduce(lambda d, key: d[key], element_heirarchy, self.__pool[module_key])
        return result

    def _validate_array_type_element(self, module_key: str,
                                     element_heirarchy: List[str],
                                     variable_to_check: Dict[str, Any]) -> bool:
        """
        Validates a __pool element when the element is an array.

        Parameters
        ----------
        module_key : str
            The module whose data is currently being validated.

        element_heirarchy : str
            The nested element heirarchy of the data being checked.

        variable_to_check : str
            A dictionary with the metadata validation guidelines.

        Returns
        -------
        bool
            Returns True if variable meets guidelines; otherwise False.
        """
        info_map = {"class": self.__class__.__name__,
                    "function": self._validate_number_element.__name__,
                    }
        value = self._get_value_from_pool(module_key, element_heirarchy)
        var_name = element_heirarchy[-1]
        if variable_to_check["minimum_length"] and variable_to_check["maximum_length"]:
            is_in_range = variable_to_check["minimum_length"] <= value <= \
                variable_to_check["maximum_length"]
            if not is_in_range:
                om.add_warning("Array out of length range.", f"{var_name=}", info_map)
            return is_in_range
        elif variable_to_check["minimum_length"]:
            is_in_range = variable_to_check["minimum_length"] <= value
            if not is_in_range:
                om.add_warning("Array out of length range.", f"{var_name=}", info_map)
            return is_in_range
        elif variable_to_check["maximum_length"]:
            is_in_range = value <= variable_to_check["maximum_length"]
            if not is_in_range:
                om.add_warning("Array out of length range.", f"{var_name=}", info_map)
            return is_in_range
        else:
            return False

    def _validate_boolean_type_element(self, module_key: str,
                                       element_heirarchy: List[str]) -> bool:
        """
        Validates a __pool boolean element.

        Parameters
        ----------
        module_key : str
            The module whose data is currently being validated.

        element_heirarchy : str
            The nested element heirarchy of the data being checked.

        variable_to_check : str
            A dictionary with the metadata validation guidelines.

        Returns
        -------
        bool
            Returns True if variable meets guidelines; otherwise False.
        """
        value = self._get_value_from_pool(module_key, element_heirarchy)
        return value in (True, False)

    def _validate_number_element(self, module_key: str,
                                 element_heirarchy: List[str],
                                 variable_to_check: Dict[str, Any]) -> bool:
        """
        Validates a __pool number element.

        Parameters
        ----------
        module_key : str
            The module whose data is currently being validated.

        element_heirarchy : str
            The nested element heirarchy of the data being checked.

        variable_to_check : str
            A dictionary with the metadata validation guidelines.

        Returns
        -------
        bool
            Returns True if variable meets guidelines; otherwise False.
        """
        info_map = {"class": self.__class__.__name__,
                    "function": self._validate_number_element.__name__,
                    }
        value = self._get_value_from_pool(module_key, element_heirarchy)
        var_name = element_heirarchy[-1]
        if variable_to_check["minimum"] and variable_to_check["maximum"]:
            is_in_range = variable_to_check["minimum"] <= value <= variable_to_check["maximum"]
            if not is_in_range:
                om.add_warning("Value out of range.", f"{var_name=}", info_map)
            return is_in_range
        elif variable_to_check["minimum"]:
            is_in_range = variable_to_check["minimum"] <= value
            if not is_in_range:
                om.add_warning("Value out of range.", f"{var_name=}", info_map)
            return is_in_range
        elif variable_to_check["maximum"]:
            is_in_range = value <= variable_to_check["maximum"]
            if not is_in_range:
                om.add_warning("Value out of range.", f"{var_name=}", info_map)
            return is_in_range
        else:
            return True

    def _validate_string_element(self, module_key: str,
                                 element_heirarchy: List[str],
                                 variable_to_check: Dict[str, Any]) -> bool:
        """
        Validates a __pool string element.

        Parameters
        ----------
        module_key : str
            The module whose data is currently being validated.

        element_heirarchy : str
            The nested element heirarchy of the data being checked.

        variable_to_check : str
            A dictionary with the metadata validation guidelines.

        Returns
        -------
        bool
            Returns True if variable meets guidelines; otherwise False.
        """
        info_map = {"class": self.__class__.__name__,
                    "function": self._validate_string_element.__name__,
                    }
        value = self._get_value_from_pool(module_key, element_heirarchy)
        var_name = element_heirarchy[-1]
        if variable_to_check["pattern"]:
            is_match = bool(re.match(variable_to_check["pattern"], value))
            if not is_match:
                om.add_warning(f"String variable must match pattern {variable_to_check['pattern']}.",
                               f"{var_name=}",
                               info_map)
            return is_match
        else:
            om.add_error("Metadata must have pattern to match string to.", f"{var_name=}", info_map)
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

# !/usr/bin/env python3

import json

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
                if self._validate_element(variable, value):
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

    def _validate_element(self, key: str, value: Any) -> bool:
        """
        Perform data validation checks.

        Parameters
        ----------
        key : str
            The key of the data to validate.

        value : Any
            The value of the data to validate.


        Returns
        -------
        bool
            True if the data is valid, False otherwise.
        """
        # Perform data validation checks
        # Return True if the data is valid, False otherwise

        # TODO in validate_element fun branch
        # where element is found to be invalid, place this warning:
        # om.add_warning("Invalid data", f"Invalid data found: {key=}; {value=}", info_map)
        pass

    def _fix_data(self, module_key: str, variable_name: str, value: Any) -> bool:
        """
        Attempt to fix the invalid data.

        Parameters
        ----------
        module_key : str
            The key of the module which the data to fix belongs to

        variable_name : str
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
        info_map = {"class": self.__class__.__name__,
                    "function": self._validate_data.__name__,
                    }

        property_map_key = self.__metadata["files"][module_key]["properties"]
        default_value = self.__metadata["properties"][property_map_key]["default"]
        self.__pool[module_key][variable_name] = default_value
        om.add_warning("Data fixed", f"Invalid data fixed: {variable_name}; {value} => {default_value}", info_map)

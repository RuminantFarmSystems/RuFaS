# !/usr/bin/env python3

import csv
import json
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
        """Loads data from JSON or CSV fileRaises

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
                        om.add_log("load_data_successful", f"Successfully loaded data for {key} from {file_path}.",
                                   info_map)
                        self.__pool[key] = data
                elif details["type"] == "csv":
                    with open(file_path, "r") as csv_file:
                        data_reader = csv.DictReader(csv_file)
                        om.add_log("load_data_successful", f"Successfully loaded data for {key} from {file_path}.",
                                   info_map)
                        self.__pool[key] = list(data_reader)
                else:
                    om.add_warning("InputManager load data file is not csv/json", f"File for {key} data in path"
                                   f" {file_path} was not a csv nor json file and was not added to data pool", info_map)
            except Exception as e:
                raise e

    def _validate_data(self, eager_termination: bool = True) -> bool:
        """
        Validates input data

        Args
        ----
        eager_termination : bool, optional
            Flag to determine if the process should terminate upon finding invalid data.

        Returns
        -------
        bool
            True if all data is valid; False otherwise.
        """
        info_map = {"class": self.__class__.__name__,
                    "function": self._validate_data.__name__,
                    }
        for key, value in self.__pool.items():
            if not self._validate(key, value):
                if eager_termination:
                    om.add_error("Invalid data.", f"Invalid data found: {key} - {value}", info_map)
                    if not self._fix_data(key, value):
                        om.add_error("Data not fixable.", "Unable to fix the invalid data. Terminating the process.",
                                     info_map)
                        return False
                    else:
                        om.add_warning("Data was fixable.", f"Invalid data found: {key} - {value}", info_map)
        return True

    def _validate(self, key: str, value: Any) -> bool:
        """
        Perform data validation checks.

        Args
        ----
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
        pass

    def _fix_data(self, key: str, value: Any) -> bool:
        """
        Attempt to fix the invalid data.

        Args
        ----
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
        pass

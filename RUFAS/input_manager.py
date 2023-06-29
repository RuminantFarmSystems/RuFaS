# !/usr/bin/env python3

import csv
import json
from typing import Any, Dict

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


    def _load_metadata(self, metadata_path: str = "input/example_metadata.json") -> None:
        """
        Loads metadata from json file to IM metadata object

        Parameters
        ----------
            metadata_path : str
                The path to the metadata file
        """
        try:
            with open(metadata_path) as metadata_file:
                self.__metadata = json.load(metadata_file)

        except Exception as e:
            raise e

    def _load_data(self) -> None:
        """Loads data from JSON or CSV file"""
        metadata_files_key = "files"
        data_files = self.__metadata[metadata_files_key]
        path_key = "path"
        info_map = {"class": self.__class__.__name__,
                    "function": self._load_data.__name__,
                    }
        for key, value in data_files.items():
            file_path = value[path_key]
            try:
                if value["type"] == "json":
                    with open(file_path) as json_file:                
                        data = json.load(json_file)  
                        self.__pool[key] = data
                if value["type"] == "csv":
                    with open(file_path, "r") as csv_file:
                        data_reader = csv.DictReader(csv_file)
                        self.__pool[key] = list(data_reader)
                else:
                    om.add_log("InputManager load data file not csv/json", f"{file_path} not csv nor json and not"
                               f" added to data pool", info_map)
                    pass
            except Exception as e:
                raise e

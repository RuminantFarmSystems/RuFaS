# !/usr/bin/env python3

import json
from typing import Any, Dict


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
            self.metadata: Dict[str, Any] = {}
            self.data: Dict[str, Any] = {}

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
                self.metadata = json.load(metadata_file)

        except Exception as e:
            raise e

    def _load_data(self) -> None:
        """Loads data from JSON or CSV file"""
        metadata_files_key = "files"
        data_files = self.metadata[metadata_files_key]
        path_key = "path"
        for key, value in data_files.items():
            file_path = value[path_key]
            try:
                with open(file_path) as file:
                    if value["type"] == "json":
                        data = json.load(file)  
                        self.__pool[key] = data
                    if value["type"] == "csv":
                        # TODO handle csv as well
                        pass
                    else:
                        pass
                        # TODO add error or log?
            except Exception as e:
                raise e

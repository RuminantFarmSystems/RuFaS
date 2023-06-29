# !/usr/bin/env python3

import json
from typing import Any, Dict, Optional


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

    def load_metadata(self, metadata_path: str) -> None:
        """
        Loads metadata from json file to IM metadata object

        Parameters
        ----------
            metadata_path : str
                The path to the metadata file
        """
        with open(metadata_path) as metadata_file:
            self.__metadata = json.load(metadata_file)


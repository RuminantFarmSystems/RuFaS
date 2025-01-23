from typing import Any

from .crop_data import CropData


class CropDataFactory:
    """
    Manages and manufactures CropData instances using user-input crop configurations.

    Attributes
    ----------
    _crop_configurations : dict[str, dict[str, Any]]
        Maps names of different crop configurations to dictionaries of their attributes.

    """

    _crop_configurations: dict[str, dict[str, Any]]

    @classmethod
    def setup_crop_configurations(cls) -> None:
        pass

    @classmethod
    def create_crop_data(cls, crop_type: str) -> CropData:
        pass

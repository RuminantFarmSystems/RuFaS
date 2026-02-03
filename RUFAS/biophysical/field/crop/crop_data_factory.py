from typing import Any, TypedDict

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager

from RUFAS.biophysical.field.crop.crop_data import CropData, PlantCategory


class CropConfiguration(TypedDict):
    """
    Data structure used to store crop configuration attributes. Attribute descriptions are omitted because all
    attributes are documented in both the metadata properties and the CropData class docstring.
    """

    name: str
    plant_category: PlantCategory
    is_nitrogen_fixer: bool
    minimum_temperature: float
    optimal_temperature: float
    potential_heat_units: float
    max_leaf_area_index: float
    first_heat_fraction_point: float
    first_leaf_fraction_point: float
    second_heat_fraction_point: float
    second_leaf_fraction_point: float
    senescent_heat_fraction: float
    light_use_efficiency: float
    emergence_nitrogen_fraction: float
    half_mature_nitrogen_fraction: float
    mature_nitrogen_fraction: float
    emergence_phosphorus_fraction: float
    half_mature_phosphorus_fraction: float
    mature_phosphorus_fraction: float
    max_root_depth: float
    root_distribution_param_da: float
    root_distribution_param_c: float
    optimal_harvest_index: float
    minimum_harvest_index: float
    dry_matter_percentage: float
    lignin_dry_matter_percentage: float
    crude_protein_percent_at_harvest: float
    non_protein_nitrogen_at_harvest: float
    starch_at_harvest: float
    adf_at_harvest: float
    ndf_at_harvest: float
    sugar_at_harvest: float
    ash_at_harvest: float
    yield_nitrogen_fraction: float
    yield_phosphorus_fraction: float


class CropDataFactory:
    """
    Manages and manufactures CropData instances using user-input crop configurations.

    Attributes
    ----------
    _crop_configurations : dict[str, CropConfiguration]
        Maps names of different crop configurations to dictionaries of their attributes.
    _om : OutputManager
        OutputManager instance.

    """

    _crop_configurations: dict[str, CropConfiguration]
    _om: OutputManager

    @classmethod
    def setup_crop_configurations(cls) -> None:
        """
        Collects crop configuration inputs, validates them, and stores them so they can be used for creating CropData.

        Raises
        ------
        ValueError
            If the names of crop configurations are not unique.
        """
        cls._crop_configurations = {}
        cls._om = OutputManager()

        im = InputManager()
        unprocessed_crop_configurations = im.get_data("crop_configurations.crop_configurations")

        if unprocessed_crop_configurations:
            for config in unprocessed_crop_configurations:
                crop_config = cls._manufacture_crop_configuration(config)
                if (name := crop_config["name"]) in cls._crop_configurations.keys():
                    info_map = {
                        "class": cls.__name__,
                        "function": cls.setup_crop_configurations.__name__,
                        "name": name,
                    }
                    err_name = "Duplicate crop configuration name."
                    err_msg = f"{name=} is used for more than one crop configuration."
                    cls._om.add_error(err_name, err_msg, info_map)
                    raise ValueError(f"{err_name} {err_msg}")
                cls._crop_configurations[name] = crop_config

    @classmethod
    def _manufacture_crop_configuration(cls, config: dict[str, Any]) -> CropConfiguration:
        """
        Creates and validates the configuration for a single crop.

        Parameters
        ----------
        config : dict[str, Any]
            A dictionary containing the configuration attributes for a single crop.

        Returns
        -------
        CropConfiguration
            A validated crop configuration dictionary.

        Raises
        ------
        ValueError
            If the crop type is not valid for the crop category.

        """
        plant_category = PlantCategory(config["plant_category"])

        config["plant_category"] = plant_category

        new_config: CropConfiguration = CropConfiguration(**config)
        return new_config

    @classmethod
    def get_available_crop_configurations(cls) -> list[str]:
        """
        Returns a list of the names of the available crop configurations.

        Returns
        -------
        list[str]
            A list of the names of the available crop configurations.

        """
        return list(cls._crop_configurations.keys())

    @classmethod
    def get_full_crop_configurations(cls) -> dict[str, CropConfiguration]:
        """Returns the full crop configurations available in the simulation."""
        return cls._crop_configurations

    @classmethod
    def create_crop_data(cls, crop_type: str) -> CropData:
        """
        Creates a CropData instance configured with the attributes of the specified crop configuration.

        Parameters
        ----------
        crop_type : str
            The name of the crop configuration to use.

        Returns
        -------
        CropData
            A CropData instance with the attributes of the specified crop configuration.

        Raises
        ------
        ValueError
            If the specified crop configuration does not exist.

        """
        if crop_type not in cls._crop_configurations.keys():
            info_map = {
                "class": cls.__name__,
                "function": cls.create_crop_data.__name__,
                "crop_type": crop_type,
            }
            err_name = "Invalid crop configuration."
            err_msg = f"{crop_type=} is not a valid crop configuration."
            cls._om.add_error(err_name, err_msg, info_map)
            raise ValueError(f"{err_name} {err_msg}")

        return CropData(**cls._crop_configurations[crop_type])

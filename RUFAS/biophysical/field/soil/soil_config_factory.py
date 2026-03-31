import dataclasses
from enum import Enum

from RUFAS.biophysical.field.soil.soil_data import SoilData


class SoilConfiguration(Enum):
    """Enum of all currently support soil configurations"""

    GENERIC = "generic"


class SoilConfigFactory:
    """
    This module serves as a way to easily create and modify SoilData objects based on a set of given configurations. It
    is based on the CropSpeciesDataFactory model, and should contain all equivalent functionalities.

    """

    @staticmethod
    def create_soil_data(
        field_size: float,
        config: SoilConfiguration = SoilConfiguration("generic"),
        **kwargs,
    ) -> SoilData:
        """
        Creates a soil data object from a SoilConfiguration enum, with the defaults from that configurations and the
        optional ability to modify attributes.

        Parameters
        ----------
        field_size : float
            Size of the field. Used to initialize a Soil object for this module to work with, if a pre-configured
            SoilData object is not provided (ha).
        config : SoilConfiguration
            Configuration of the soil.

        Returns
        -------
        SoilData
            A Soildata object.

        """
        configuration_by_type = {SoilConfiguration.GENERIC: SoilData}
        config_class = configuration_by_type[config]
        config_instance = config_class(field_size=field_size)

        # handle any attributes that need to be modified
        if kwargs:
            attribute_list = dataclasses.asdict(config_instance).keys()

            # update all valid attributes
            for attribute, value in kwargs.items():
                if attribute in attribute_list:
                    setattr(config_instance, attribute, value)
                else:
                    raise AttributeError(f"{attribute} is not a valid attribute of SoilData")

        return config_instance

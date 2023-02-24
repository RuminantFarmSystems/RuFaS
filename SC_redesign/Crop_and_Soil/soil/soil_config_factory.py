from enum import Enum
import dataclasses
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData

"""
This module serves as a way to easily create and modify SoilData objects based on a set of given configurations. It is 
based on the CropSpeciesDataFactory model, and should contain all equivalent functionalities.
"""


class SoilConfigurations(Enum):
    """Enum of all currently support soil configurations"""
    GENERIC = "generic"
    # TODO: implement additional soil types


class SoilConfigFactory:
    @staticmethod
    def create_soil_data(config: SoilConfigurations = SoilConfigurations("generic"), **kwargs) -> SoilData:
        """Creates a soil data object from a SoilConfiguration enum, with the defaults from that configurations and the
            optional ability to modify attributes
        """
        configuration_by_type = {
            SoilConfigurations.GENERIC: SoilData
        }
        config_class = configuration_by_type[config]
        config_instance = config_class()

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

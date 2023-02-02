from enum import Enum
import dataclasses
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData, Corn, Alfalfa, CerealRye, FallOats, Potato, Soybean
from SC_redesign.Crop_and_Soil.crop.crop_data import SpringBarley, SpringWheat, SugarBeet, TallFescue, Triticale
from SC_redesign.Crop_and_Soil.crop.crop_data import WinterWheat

class CropSpecies(Enum):
    """Enum of all the crop types supported by RUFAS"""
    GENERIC = "generic"  # generic crop
    CORN = "corn"
    ALFALFA = "alfalfa"
    CEREAL_RYE = "cereal_rye"
    FALL_OATS = "fall_oats"
    POTATO = "potato"
    SOYBEAN = "soybean"
    SPRING_BARLEY = "spring_barley"
    SPRING_WHEAT = "spring_wheat"
    SUGAR_BEET = "sugar_beet"
    TALL_FESCUE = "tall_fescue"
    TRITICALE = "triticale"
    WINTER_WHEAT = "winter_wheat"


class CropSpeciesDataFactory:
    @staticmethod
    def create_species_data(species: CropSpecies = CropSpecies("generic"), **kwargs) -> CropData:
        """Create a species data object from a CropSpecies enum, with species defaults and the optional ability to
        modify additional attributes."""
        species_by_type = {
            CropSpecies.GENERIC: CropData,
            CropSpecies.CORN: Corn,
            CropSpecies.ALFALFA: Alfalfa,
            CropSpecies.CEREAL_RYE: CerealRye,
            CropSpecies.FALL_OATS: FallOats,
            CropSpecies.POTATO: Potato,
            CropSpecies.SOYBEAN: Soybean,
            CropSpecies.SPRING_BARLEY: SpringBarley,
            CropSpecies.SPRING_WHEAT: SpringWheat,
            CropSpecies.SUGAR_BEET: SugarBeet,
            CropSpecies.TALL_FESCUE: TallFescue,
            CropSpecies.TRITICALE: Triticale,
            CropSpecies.WINTER_WHEAT: WinterWheat
        }
        species_class = species_by_type[species]
        species_instance = species_class()

        # handle additional attribute specifications
        if kwargs:
            attr_list = dataclasses.asdict(species_instance).keys()

            # update valid attributes
            for attribute, value in kwargs.items():
                if attribute in attr_list:
                    setattr(species_instance, attribute, value)
                else:
                    raise AttributeError(f"{attribute} is not a valid attribute of CropData")

            # set new name to indicate that the class has been altered.
            name_key_absent = "name" not in kwargs.keys()
            id_is_only_key = (len(kwargs) == 1 and "id" in kwargs.keys())
            if name_key_absent and not id_is_only_key:
                species_instance.name = species_instance.name.replace("default", "altered")

        return species_instance


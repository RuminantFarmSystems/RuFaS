from enum import Enum
import dataclasses
from RUFAS.routines.field.crop.crop_data import CropData
from RUFAS.routines.field.crop.crop_configurations.alfalfa import AlfalfaHay, AlfalfaSilage, AlfalfaBaleage
from RUFAS.routines.field.crop.crop_configurations.cereal_rye import (
    CerealRyeHay, CerealRyeGrain, CerealRyeSilage, CerealRyeBaleage
)
from RUFAS.routines.field.crop.crop_configurations.corn import CornGrain, CornSilage
from RUFAS.routines.field.crop.crop_configurations.soybean import SoybeanHay, SoybeanGrain
from RUFAS.routines.field.crop.crop_configurations.tall_fescue import TallFescueHay, TallFescueSilage, TallFescueBaleage
from RUFAS.routines.field.crop.crop_configurations.triticale import (
    TriticaleHay, TriticaleGrain, TriticaleSilage, TriticaleBaleage
)
from RUFAS.routines.field.crop.crop_configurations.winter_wheat import (
    WinterWheatHay, WinterWheatGrain, WinterWheatSilage, WinterWheatBaleage
)


class CropSpecies(Enum):
    """Enum of all the crop types supported by RUFAS"""
    ALFALFA_HAY = "alfalfa_hay"
    ALFALFA_SILAGE = "alfalfa_silage"
    ALFALFA_BALEAGE = "alfalfa_baleage"
    CEREAL_RYE_HAY = "cereal_rye_hay"
    CEREAL_RYE_GRAIN = "cereal_rye_grain"
    CEREAL_RYE_SILAGE = "cereal_rye_silage"
    CEREAL_RYE_BALEAGE = "cereal_rye_baleage"
    CORN_GRAIN = "corn_grain"
    CORN_SILAGE = "corn_silage"
    SOYBEAN_HAY = "soybean_hay"
    SOYBEAN_GRAIN = "soybean_grain"
    TALL_FESCUE_HAY = "tall_fescue_hay"
    TALL_FESCUE_SILAGE = "tall_fescue_silage"
    TALL_FESCUE_BALEAGE = "tall_fescue_baleage"
    TRITICALE_HAY = "triticale_hay"
    TRITICALE_GRAIN = "triticale_grain"
    TRITICALE_SILAGE = "triticale_silage"
    TRITICALE_BALEAGE = "triticale_baleage"
    WINTER_WHEAT_HAY = "winter_wheat_hay"
    WINTER_WHEAT_GRAIN = "winter_wheat_grain"
    WINTER_WHEAT_SILAGE = "winter_wheat_silage"
    WINTER_WHEAT_BALEAGE = "winter_wheat_baleage"


class CropSpeciesDataFactory:
    """
    Creates a species data object from a CropSpecies enum

    """
    @staticmethod
    def create_species_data(species: CropSpecies = CropSpecies("corn_grain"), **kwargs) -> CropData:
        """
        Creates a species data object from a CropSpecies enum, with species defaults and the optional ability to modify
        additional attributes.

        Parameters
        ----------
        species : CropSpecies
            An enum value representing the crop species, defaults to CropSpecies("corn_grain").
        **kwargs
            Additional keyword arguments for setting or overriding attributes in the `CropData` object.

        Returns
        -------
        CropData
            A `CropData` object initialized with species-specific defaults and any modifications specified through
            kwargs.

        """
        species_by_type = {
            CropSpecies.ALFALFA_HAY: AlfalfaHay,
            CropSpecies.ALFALFA_SILAGE: AlfalfaSilage,
            CropSpecies.ALFALFA_BALEAGE: AlfalfaBaleage,
            CropSpecies.CEREAL_RYE_HAY: CerealRyeHay,
            CropSpecies.CEREAL_RYE_GRAIN: CerealRyeGrain,
            CropSpecies.CEREAL_RYE_SILAGE: CerealRyeSilage,
            CropSpecies.CEREAL_RYE_BALEAGE: CerealRyeBaleage,
            CropSpecies.CORN_GRAIN: CornGrain,
            CropSpecies.CORN_SILAGE: CornSilage,
            CropSpecies.SOYBEAN_HAY: SoybeanHay,
            CropSpecies.SOYBEAN_GRAIN: SoybeanGrain,
            CropSpecies.TALL_FESCUE_HAY: TallFescueHay,
            CropSpecies.TALL_FESCUE_SILAGE: TallFescueSilage,
            CropSpecies.TALL_FESCUE_BALEAGE: TallFescueBaleage,
            CropSpecies.TRITICALE_HAY: TriticaleHay,
            CropSpecies.TRITICALE_GRAIN: TriticaleGrain,
            CropSpecies.TRITICALE_SILAGE: TriticaleSilage,
            CropSpecies.TRITICALE_BALEAGE: TriticaleBaleage,
            CropSpecies.WINTER_WHEAT_HAY: WinterWheatHay,
            CropSpecies.WINTER_WHEAT_GRAIN: WinterWheatGrain,
            CropSpecies.WINTER_WHEAT_SILAGE: WinterWheatSilage,
            CropSpecies.WINTER_WHEAT_BALEAGE: WinterWheatBaleage,
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
            # If only the id is being changed, the crop is still a default so its name should not be changed
            if name_key_absent and not id_is_only_key:
                species_instance.name = "altered" + species_instance.name

        return species_instance

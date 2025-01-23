from enum import Enum


# TODO: deprecate this.
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

    def __str__(self):
        return str(self.value)

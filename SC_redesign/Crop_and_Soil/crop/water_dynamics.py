from SC_redesign.Crop_and_Soil.soil.soil import Soil


class WaterDynamics:
    def __init__(self):
        self.evaporation = None
        self.transpiration = None
        self.evapotranspiration = None
        self.evapotranspiration_max = None
        self.water_deficiency = None

    def cycle_water(self, soil: Soil):
        self.update_evaporation(soil)
        self.update_transpiration(soil)
        self.update_max_evapotranspiration(soil)
        self.update_evapotranspiration()
        self.assess_water_deficiency()

    def update_evaporation(self, soil: Soil) -> None:  # TODO: need to make sure it makes sense to keep these values in soil
        """update evaporation by copying it from the soil class"""
        self.evaporation = soil.evaporation

    def update_transpiration(self, soil: Soil) -> None:  # TODO: need to make sure it makes sense to keep these values in soil
        """update transpiration by copying it from the soil class"""
        self.transpiration = soil.transpiration

    def update_max_evapotranspiration(self, soil: Soil) -> None:  # TODO: need to make sure it makes sense to keep these values in soil
        self.evapotranspiration_max = soil.evapotranspiration_max

    def update_evapotranspiration(self) -> None:
        self.evapotranspiration = calc_evapotranspiration(self.evaporation, self.transpiration)

    def assess_water_deficiency(self):
        self.water_deficiency = calc_water_deficiency(self.evapotranspiration, self.evapotranspiration_max)


# ---- helper functions ----
def calc_evapotranspiration(evaporation: float, transpiration: float) -> float:  # TODO: belongs in Soil class?
    """
    Description: calculate the annual evapotranspiration #TODO: why is this 'annual' routine executed every day?

    Args:
        evaporation: annual evaporation
        transpiration: annual transpiration

    Returns: total evapotranspiration
    """
    return evaporation + transpiration


def calc_water_deficiency(evapotrans: float, evapotrans_max: float) -> float:  # pseudocode: C.9.C.1
    """
    Description: calculate water deficiency factor

    Args:
        evapotrans: annual evapotranspiration
        evapotrans_max: maximum annual evapotranspiration

    Returns: water deficiency factor
    """
    if evapotrans_max != 0:
        return 100 * (evapotrans / evapotrans_max)
    else:
        return 0

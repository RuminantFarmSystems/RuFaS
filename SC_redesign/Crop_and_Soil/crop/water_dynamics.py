from SC_redesign.Crop_and_Soil.soil.soil import Soil


class WaterDynamics:
    def __init__(self):
        self.evaporation = None
        self.transpiration = None
        self.evapotranspiration = None
        self.evapotranspiration_max = None
        self.water_deficiency = None

    def cycle_water(self, evaporation: float, transpiration: float, max_evapotranspiration: float) -> None:
        self.evaporation = evaporation
        self.transpiration = transpiration
        self.set_max_evapotranspiration(max_evapotranspiration)
        self.update_evapotranspiration()
        self.assess_water_deficiency()

    def set_max_evapotranspiration(self, max_evapotranspiration: float) -> None:
        self.evapotranspiration_max = max_evapotranspiration

    def update_evapotranspiration(self) -> None:
        self.evapotranspiration = self.calc_evapotranspiration(self.evaporation, self.transpiration)

    def assess_water_deficiency(self) -> None:
        self.water_deficiency = self.calc_water_deficiency(self.evapotranspiration, self.evapotranspiration_max)

    @staticmethod
    def calc_evapotranspiration(evaporation: float, transpiration: float) -> float:  # TODO: belongs in Soil class?
        """
        Description: calculate the annual evapotranspiration #TODO: why is this 'annual' routine executed every day?

        Args:
            evaporation: annual evaporation
            transpiration: annual transpiration

        Returns: total evapotranspiration
        """
        return evaporation + transpiration

    @staticmethod
    def calc_water_deficiency(evapotranspiration: float, max_evapotranspiration: float) -> float:  # pseudocode: C.9.C.1
        """
        Description: calculate water deficiency factor

        Args:
            evapotranspiration: annual evapotranspiration
            max_evapotranspiration: maximum annual evapotranspiration

        Returns: water deficiency factor
        """
        if max_evapotranspiration != 0:
            return 100 * (evapotranspiration / max_evapotranspiration)
        else:
            return 0

    # TODO: Further functions in RUFAS/routines/field/crop/transpiration.py need to be translated (into soil methods?)

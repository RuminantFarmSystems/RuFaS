from SC_redesign.Crop_and_Soil.soil.soil import Soil
from typing import Optional
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData


class WaterDynamics:
    def __init__(self, crop_data: Optional[CropData] = None):
        self.data = crop_data or CropData()  # initialize with defaults, if not given

    def cycle_water(self, evaporation: float, transpiration: float, max_evapotranspiration: float) -> None:
        self.data.cumulative_evaporation = evaporation
        self.data.cumulative_transpiration = transpiration
        self.data.max_cumulative_evapotranspiration = max_evapotranspiration
        self.data.cumulative_evapotranspiration = self._determine_evapotranspiration(self.data.cumulative_evaporation,
                                                                                     self.data.cumulative_transpiration)
        self.data.water_deficiency = self._determine_water_deficiency(self.data.cumulative_evapotranspiration,
                                                                      self.data.max_cumulative_evapotranspiration)

    @staticmethod
    def _determine_evapotranspiration(evaporation: float, transpiration: float) -> float:  # TODO: belongs in Soil class?
        """
        Description: calculate the annual evapotranspiration #TODO: why is this 'annual' routine executed every day?

        Args:
            evaporation: evaporation
            transpiration: transpiration

        Returns: total evapotranspiration
        """
        return evaporation + transpiration

    @staticmethod
    def _determine_water_deficiency(evapotranspiration: float, max_evapotranspiration: float) -> float:  # pseudocode: C.9.C.1
        """
        Description: calculate water deficiency factor

        SWAT Reference: 5:3.3

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

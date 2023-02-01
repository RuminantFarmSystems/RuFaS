from math import exp
from typing import Optional
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData

"""
This module primarily follows the Growth Constraints section of the SWAT model (5:3.1)
"""


class GrowthConstraints:
    """crop process class pertaining to growth constraints"""
    def __init__(self, crop_data: Optional[CropData] = None):
        self.data = crop_data or CropData()  # initialize with defaults, if not given

    def constrain_growth(self, max_transpiration: float, temperature: float) -> None:
        """ main method; constrains a plant's growth by updating stress and growth factor values

        Args:
            max_transpiration: the maximum amount of transpiration (mm) possible (determined by soil) on this day
            temperature: the current air temperature (Celsius)
        """

        self.data.water_stress = GrowthConstraints._determine_water_stress(self.data.water_uptake, max_transpiration)
        #  TODO: plant transpiration should be an attribute of the crop (in addition to the soil?)

        self.data.temp_stress = GrowthConstraints._determine_temperature_stress(temperature,
                                                                                self.data.minimum_temperature,
                                                                                self.data.optimal_temperature)
        self.data.nitrogen_stress = GrowthConstraints._determine_nutrient_stress(self.data.nitrogen,
                                                                                 self.data.optimal_nitrogen)
        self.data.phosphorus_stress = GrowthConstraints._determine_nutrient_stress(self.data.phosphorus,
                                                                                   self.data.optimal_phosphorus)
        self.data.growth_factor = GrowthConstraints._determine_growth_factor(self.data.water_stress,
                                                                             self.data.temp_stress,
                                                                             self.data.nitrogen_stress,
                                                                             self.data.phosphorus_stress)


    @staticmethod
    def _determine_growth_factor(water_stress: float, temperature_stress: float, nitrogen_stress: float,
                                 phosphorus_stress: float) -> float:  # pseudocode: C.7.E.1
        """
        Description: Calculates plant growth factor

        Args:
            water_stress: plant water stress
            temperature_stress: plant temperature stress
            nitrogen_stress: plant nitrogen stress
            phosphorus_stress: plant phosphorus stress

        SWAT Reference: 5:3.2.3

        Returns: plant growth factor
        """
        return 1.0 - max(water_stress, temperature_stress, nitrogen_stress, phosphorus_stress)

    @staticmethod
    def _determine_water_stress(water_uptake: float, max_transpiration: float) -> float:  # pseudocode: C.7.A.1
        """
        Description: Calculates water stress for a given day.

        Args:
            water_uptake: the water taken up by the plant from the soil
            max_transpiration: the maximum plant transpiration on a given day

        SWAT Reference: 5:3.1.1

        Returns: the plant's water stress
        """
        if max_transpiration == 0:  # avoid division by zero
            return 0

        stress = 1 - (water_uptake / max_transpiration)
        stress = max(0., stress)  # constrain to 0
        stress = min(1., stress)  # constrain to 1

        return stress

    @staticmethod
    def _determine_temperature_stress(air_temp: float, min_temp: float, optimal_temp: float) -> float:  # pseudocode C.7.B.
        """
        Description: Calculates temperature stress for a given day.

        Args:
            air_temp: average air temperature (Celsius)
            min_temp: minimum temperature for plant growth (Celsius)
            optimal_temp: optimal temperature for plant growth (Celsius)

        SWAT Reference: 5:3.1.2

        Returns: the plant's temperature stress
        """

        numerator = -0.1054 * (optimal_temp - air_temp)**2
        double_diff = 2*optimal_temp - min_temp

        if min_temp < air_temp <= optimal_temp:
            stress = 1 - exp(numerator / (air_temp - min_temp)**2)

        elif optimal_temp < air_temp <= double_diff:
            stress = 1 - exp(numerator / (double_diff - min_temp)**2)

        else:
            stress = 1

        return stress

    @staticmethod
    def _determine_nutrient_stress(stored: float, optimal: float) -> float:  # pseudocode C.7.C.2
        """
        Description: Calculates plant nutrient stress for the day.

        Args:
            stored: the mass of the nutrient currently stored in the plant
            optimal: the optimal mass of the nutrient stored in the plant

        SWAT Reference: 5:3.1.3, 5:3.1.4

        Returns: nutrient stress
        """
        if optimal == 0:
            stress = 0
        else:
            stress_factor = 200 * (stored / optimal - 0.5)
            stress = 1 - stress_factor / (stress_factor + exp(3.535 - 0.02597 * stress_factor))
        return min(1, stress)

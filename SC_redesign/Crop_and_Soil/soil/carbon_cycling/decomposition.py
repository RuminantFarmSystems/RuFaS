import math
from typing import Optional

from SC_redesign.Crop_and_Soil.soil import soil_data
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData


class Decomposition:
    def __init__(self, soil_data: Optional[SoilData] = None):
        self.data = soil_data or SoilData()  # initialize with defaults, if not given

    def decomposite(self, soil, weather, time):
        """
        Description: calculates temperature and moisture decomposition factors for
            Carbon based on weather and soil profile.
            "pseudocode_soil" S.6.A
        Args:
            soil: an instance of the Soil class defined in soil.py
            weather: an instance of the Weather class defined in classes.py
            time: an instance of the Time class defined in classes.py
        """
        self.data.decomposition_temperature_effect = self.temp_factor(soil, weather, time)

        self.data.decomposition_moisture_effect = self.moisture_factor(soil)

    @staticmethod
    def calc_temp_factor(temp_average: float) -> float:
        """
        Description: calculates the Temperature factor for carbon decomposition
            "pseudocode_soil" S.6.A.1
            defaults drawn from defac: course soil
        Args:
            temp_average:
        """
        decomposition_inflection_x = 15.400
        decomposition_inflection_y = 11.750
        max_min_distance = 29.700
        inflection_slope = 0.03
        normalizer = 20.80546

        # S.6.A.4
        return max(0.0,
                   (decomposition_inflection_y + (max_min_distance / math.pi) * math.atan(math.pi * inflection_slope * (
                           temp_average - decomposition_inflection_x))) / normalizer)

    @staticmethod
    def moisture_factor(soil) -> float:
        """
        Description: calculates the moisture factor for carbon decomposition
            "pseudocode_soil" S.6.A.2
            defaults drawn from defac: course soil
        Args:
            soil
        """
        a = 0.55
        b = 1.7
        c = -0.007
        e1 = 6.648115
        e2 = 3.22

        for layer in soil.soil_layers:
            # S.6.A.5
            base_1 = (layer.water_fac - b) / (a - b)
            base_2 = (layer.water_fac - c) / (a - c)
            hold = (base_1 ** e1) * (base_2 ** e2)

        return hold

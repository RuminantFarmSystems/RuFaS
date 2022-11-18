from math import exp


class GrowthConstraints:
    """crop process class pertaining to growth constraints"""
    def __init__(self):
        self.water_uptake = 18
        self.nitrogen = 35
        self.optimal_nitrogen = 100
        self.phosphorus = 20
        self.optimal_phosphorus = 80
        self.minimum_temperature = 15
        self.optimal_temperature = 22

        self.growth_factor = 1.0
        self.water_stress = None
        self.temp_stress = None
        self.nitrogen_stress = None
        self.phosphorus_stress = None

    def constrain_growth(self, max_trans: float, temp: float) -> None:
        """
        Description: constrain a crops growth by updating its stress and growth factor values

        Args:
            max_trans: the maximum amount of transpiration (mm) possible (determined by soil) on this day
            temp: the current air temperature (Celsius)
        """
        self.assess_water_stress(max_trans)
        self.assess_temp_stress(temp)
        self.assess_nitrogen_stress()
        self.assess_phosphorus_stress()
        self.determine_growth_factor()

    def assess_water_stress(self, max_transpiration: float) -> None:
        #  TODO: plant transpiration should be an attribute of the crop (in addition to the soil?)
        self.water_stress = calc_water_stress(self.water_uptake, max_transpiration)

    def assess_temp_stress(self, temperature: float) -> None:
        self.temp_stress = calc_temperature_stress(temperature, self.minimum_temperature, self.optimal_temperature)

    def assess_nitrogen_stress(self) -> None:
        self.nitrogen_stress = calc_nutrient_stress(self.nitrogen, self.optimal_nitrogen)

    def assess_phosphorus_stress(self) -> None:
        self.phosphorus_stress = calc_nutrient_stress(self.phosphorus, self.optimal_phosphorus)

    def determine_growth_factor(self) -> None:
        self.growth_factor = calc_growth_factor(self.water_stress, self.temp_stress, self.nitrogen_stress,
                                                self.phosphorus_stress)


def calc_growth_factor(water_stress: float, temperature_stress: float, nitrogen_stress: float,
                       phosphorus_stress: float) -> float:  # pseudocode: C.7.E.1
    """
    Description: Calculates plant growth factor

    Args:
        water_stress: plant water stress
        temperature_stress: plant temperature stress
        nitrogen_stress: plant nitrogen stress
        phosphorus_stress: plant phosphorus stress

    Returns: plant growth factor
    """
    return 1.0 - max(water_stress, temperature_stress, nitrogen_stress, phosphorus_stress)


def calc_water_stress(water_uptake: float, max_transpiration: float) -> float:  # pseudocode: C.7.A.1
    """
    Description: Calculates water stress for a given day.

    Args:
        water_uptake: the water taken up by the plant from the soil
        max_transpiration: the maximum plant transpiration on a given day

    Returns: the plant's water stress
    """
    if max_transpiration == 0:  # avoid division by zero
        return 0

    stress = 1 - (water_uptake / max_transpiration)
    stress = max(0., stress)  # constrain to 0
    stress = min(1., stress)  # constrain to 1

    return stress


def calc_temperature_stress(air_temp: float, min_temp: float, optimal_temp: float) -> float:  # pseudocode C.7.B.
    """
    Description: Calculates temperature stress for a given day.

    Args:
        air_temp: average air temperature (Celsius)
        min_temp: minimum temperature for plant growth (Celsius)
        optimal_temp: optimal temperature for plant growth (Celsius)

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


def calc_nutrient_stress(stored: float, optimal: float) -> float:  # pseudocode C.7.C.2
    """
    Description: Calculates plant nutrient stress for the day.

    Args:
        stored: the mass of the nutrient currently stored in the plant
        optimal: the optimal mass of the nutrient stored in the plant

    Returns: nutrient stress
    """
    if optimal == 0:
        stress = 0
    else:
        stress_factor = 200 * (stored / optimal - 0.5)
        stress = 1 - stress_factor / (stress_factor + exp(3.535 - 0.02597 * stress_factor))
    return min(1, stress)

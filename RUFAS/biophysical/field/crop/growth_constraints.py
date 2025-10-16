from math import exp
from typing import Optional

from RUFAS.biophysical.field.crop.crop_data import CropData


class GrowthConstraints:
    """
    A class pertaining to growth constraints of crops.

    This class is focused on managing and applying growth constraints to crop processes, as described in the Growth
    Constraints section of the SWAT model (5:3.1). It uses data from the `CropData` class to assess and apply these
    constraints.

    Parameters
    ----------
    crop_data : Optional[CropData], optional
        A `CropData` object containing crop specifications and tracked attributes. If not provided,
        a default `CropData` object is initialized with default values.
    water_stress : float, default 0.0
        Water stress for the day (unitless).
    temp_stress : Optional[float], default None
        Temperature stress for the day (unitless).
    nitrogen_stress : Optional[float], default None
        Nitrogen stress for the day (unitless).
    phosphorus_stress : Optional[float], default None
        Phosphorus stress for the day (unitless).

    Attributes
    ----------
    data : CropData
        A reference to the `crop_data` object on which the growth constraint operations are conducted.
    water_stress : float
        Water stress for the day (unitless).
    temp_stress : Optional[float]
        Temperature stress for the day (unitless).
    nitrogen_stress : Optional[float]
        Nitrogen stress for the day (unitless).
    phosphorus_stress : Optional[float]
        Phosphorus stress for the day (unitless).

    Methods
    -------
    constrain_growth(max_transpiration: float, temperature: float) -> None
        Constrain a plant's growth by updating stress and growth factor values based on maximum transpiration
        and current air temperature.

    _determine_growth_factor(water_stress: float, temperature_stress: float, nitrogen_stress: float,
                             phosphorus_stress: float) -> float
        Calculate the plant growth factor based on various stress parameters.

    _determine_water_stress(water_uptake: float, max_transpiration: float) -> float
        Calculate water stress for a given day based on water uptake and maximum transpiration.

    _determine_temperature_stress(air_temp: float, min_temp: float, optimal_temp: float) -> float
        Calculate temperature stress for a given day based on air temperature, minimum growth temperature,
        and optimal growth temperature.

    _determine_nutrient_stress(stored: float, optimal: float) -> float
        Calculate plant nutrient stress for the day based on the amount of nutrient stored and the optimal nutrient
        amount.

    """

    def __init__(
        self,
        crop_data: Optional[CropData] = None,
        water_stress: float = 0.0,
        temp_stress: Optional[float] = None,
        nitrogen_stress: Optional[float] = None,
        phosphorus_stress: Optional[float] = None,
    ) -> None:
        self.data = crop_data or CropData()

        self.water_stress = water_stress
        self.temp_stress = temp_stress
        self.nitrogen_stress = nitrogen_stress
        self.phosphorus_stress = phosphorus_stress

    def constrain_growth(
        self,
        max_transpiration: float | None,
        temperature: float | None,
        simulate_water_stress: bool,
        simulate_temp_stress: bool,
        simulate_nitrogen_stress: bool,
        simulate_phosphorus_stress: bool,
    ) -> None:
        """
        Main method to constrain a plant's growth by updating stress and growth factor values.

        Parameters
        ----------
        max_transpiration : float | None
            The maximum amount of transpiration possible (in mm) on this day, determined by soil conditions.
        temperature : float | None
            The current air temperature in degrees Celsius.
        simulate_water_stress : bool
            Whether water stress should affect growth of all crops grown in the field.
        simulate_temp_stress : bool
            Whether temperature stress should affect growth of all crops grown in the field.
        simulate_nitrogen_stress : bool
            Whether nitrogen stress should affect growth of all crops grown in the field.
        simulate_phosphorus_stress : bool
            Whether phosphorus stress should affect growth of all crops grown in the field.

        Notes
        -----
        Each crop stressor is checked to determine whether or not it should affect crop growth. If it is not to affect
        crop growth, then the stressor is set to 0.

        """

        self.water_stress = (
            0.0
            if not simulate_water_stress
            else self._determine_water_stress(self.data.water_uptake, max_transpiration)
        )
        self.temp_stress = (
            0.0
            if not simulate_temp_stress
            else self._determine_temperature_stress(
                temperature, self.data.minimum_temperature, self.data.optimal_temperature
            )
        )
        self.nitrogen_stress = (
            0.0
            if not simulate_nitrogen_stress
            else self._determine_nutrient_stress(self.data.nitrogen, self.data.optimal_nitrogen)
        )
        self.phosphorus_stress = (
            0.0
            if not simulate_phosphorus_stress
            else self._determine_nutrient_stress(self.data.phosphorus, self.data.optimal_phosphorus)
        )

        self.data.growth_factor = self._determine_growth_factor(
            self.water_stress,
            self.temp_stress,
            self.nitrogen_stress,
            self.phosphorus_stress,
        )

    @staticmethod
    def _determine_growth_factor(
        water_stress: float,
        temperature_stress: float,
        nitrogen_stress: float,
        phosphorus_stress: float,
    ) -> float:  # pseudocode: C.7.E.1
        """
        Calculates the plant growth factor based on various stress parameters.

        Parameters
        ----------
        water_stress : float
            Plant water stress.
        temperature_stress : float
            Plant temperature stress.
        nitrogen_stress : float
            Plant nitrogen stress.
        phosphorus_stress : float
            Plant phosphorus stress.

        Returns
        -------
        float
            Calculated plant growth factor.

        References
        ----------
        SWAT 5:3.2.3
        """
        return 1.0 - max(water_stress, temperature_stress, nitrogen_stress, phosphorus_stress)

    @staticmethod
    def _determine_water_stress(water_uptake: float, max_transpiration: float) -> float:  # pseudocode: C.7.A.1
        """
        Calculates water stress for a given day.

        Parameters
        ----------
        water_uptake : float
            The water taken up by the plant from the soil (mm).
        max_transpiration : float
            The maximum plant transpiration possible on a given day (mm).

        Returns
        -------
        float
            The calculated water stress of the plant.

        References
        ----------
        SWAT 5:3.1.1
        """
        if max_transpiration == 0:  # avoid division by zero
            return 0

        stress = 1 - (water_uptake / max_transpiration)
        stress = max(0.0, stress)  # constrain to 0
        stress = min(1.0, stress)  # constrain to 1

        return stress

    @staticmethod
    def _determine_temperature_stress(
        air_temp: float, min_temp: float, optimal_temp: float
    ) -> float:  # pseudocode C.7.B.
        """
        Calculates temperature stress for a given day.

        Parameters
        ----------
        air_temp : float
            Average air temperature for the day (Celsius).
        min_temp : float
            Minimum temperature for plant growth (Celsius).
        optimal_temp : float
            Optimal temperature for plant growth (Celsius).

        Returns
        -------
        float
            The calculated temperature stress of the plant.

        References
        ----------
        SWAT 5:3.1.2
        """

        numerator = -0.1054 * (optimal_temp - air_temp) ** 2
        double_diff = 2 * optimal_temp - min_temp

        if min_temp < air_temp <= optimal_temp:
            stress = 1 - exp(numerator / (air_temp - min_temp) ** 2)

        elif optimal_temp < air_temp < double_diff:
            stress = 1 - exp(numerator / (double_diff - air_temp) ** 2)
        else:
            stress = 1

        return stress

    @staticmethod
    def _determine_nutrient_stress(stored: float, optimal: float) -> float:  # pseudocode C.7.C.2
        """
        Calculates plant nutrient stress for the day.

        Parameters
        ----------
        stored : float
            The mass of the nutrient currently stored in the plant (kg/ha).
        optimal : float
            The optimal mass of the nutrient that should be stored in the plant for ideal growth (kg/ha).

        Returns
        -------
        float
            The calculated nutrient stress of the plant.

        References
        ----------
        SWAT 5:3.1.3, 5:3.1.4
        """
        if optimal == 0:
            stress = 0
        else:
            stress_factor = 200 * (stored / optimal - 0.5)
            stress = 1 - (stress_factor / (stress_factor + exp(3.535 - (0.02597 * stress_factor))))
        return min(1, stress)

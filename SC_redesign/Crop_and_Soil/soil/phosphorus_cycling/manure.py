from typing import Optional
from math import exp, sqrt

from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from SC_redesign.Crop_and_Soil.crop_and_soil_constants import MILLIMETERS_TO_CENTIMETERS, KILOGRAMS_TO_GRAMS, \
    KILOGRAMS_TO_MILLIGRAMS, HECTARES_TO_SQUARE_CENTIMETERS, HECTARES_TO_SQUARE_MILLIMETERS, CUBIC_MILLIMETERS_TO_LITERS

"""
This module adds and tracks manure phosphorus dynamics based on the SurPhos model.
"""


class Manure:

    def __init__(self, soil_data: Optional[SoilData] = None):
        """This method initializes the SoilData object that this module will work with, or create one if none provided.

        Parameters
        ----------
        soil_data : SoilData, optional
            The SoilData object used by this module to track manure phosphorus activity, creates new one if one is not
            provided.

        """
        self.data = soil_data or SoilData()

    # --- Static Methods ---
    @staticmethod
    def _determine_temperature_factor(mean_air_temperature: float) -> float:
        """Calculates the temperature factor for the current day

        Parameters
        ----------
        mean_air_temperature : float
            The average air temperature of the current day (degrees celsius).

        Returns
        -------
        float
            The temperature factor on the current day (unitless)

        References
        ----------
        SurPhos [2], pseudocode_soil [S.5.D.I.1]

        """
        calculated_temperature_factor = ((2 * (32 ** 2) * (mean_air_temperature ** 2)) - (mean_air_temperature ** 4)) \
            / (32 ** 4)
        return min(1.0, max(0.0, calculated_temperature_factor))

    @staticmethod
    def _determine_dry_matter_decomposition_rate(temperature_factor: float) -> float:
        """Calculates the rate of manure dry matter decomposition on the current day.

        Parameters
        ----------
        temperature_factor : float
            The temperature factor on the current day (unitless)

        Returns
        -------
        float
            The rate of manure dry matter decomposition on the current day (unitless)

        References
        ----------
        SurPhos [1], pseudocode_soil [S.5.D.III.4]

        """
        return 0.003 * (temperature_factor ** 0.5)

    @staticmethod
    def _determine_dry_manure_matter_assimilation(moisture_factor: float, temperature_factor: float,
                                                  manure_cover_area: float, is_dung: bool) -> float:
        """Calculates the mass of dry manure matter applied by machine assimilated into the soil that day

        Parameters
        ----------
        moisture_factor : float
            Manure moisture factor, in range [0.0, 1.0] (unitless)
        temperature_factor : float
            The temperature factor on the current day (unitless)
        manure_cover_area : float
            Area of the field covered by manure (ha)
        is_dung : bool
            Was the manure being assimilated applied by animals grazing in the field (true / false)

        Returns
        -------
        float
            The amount of manure dry matter that is assimilated into the soil by macroinvertebrates (bioturbation) on
            the current day (kg)

        References
        ----------
        SurPhos [3, 7], pseudocode_soil [S.5.D.III.4] (Note the equation in the pseudocode is wrong)

        """
        if is_dung:
            exponential_term = exp(3.5 * sqrt(moisture_factor))
            temperature_term = temperature_factor ** 0.1
        else:
            exponential_term = exp(2.5 * moisture_factor)
            temperature_term = temperature_factor
        return (30 * exponential_term) * temperature_term * manure_cover_area

    @staticmethod
    def _determine_mineralization_rate(rate: float, temperature_factor: float, moisture_factor: float) -> float:
        """Determines the rate of mineralization of manure phosphorus on the current day.

        Parameters
        ----------
        rate : float
            The rate factor for the type of phosphorus being mineralized (unitless)
        temperature_factor : float
            The temperature factor on the current day (unitless)
        moisture_factor : float
            Manure moisture factor, in range [0.0, 1.0] (unitless)

        Returns
        -------
        float
            The rate of mineralization for a specific phosphorus pool on a given day

        References
        ----------
        SurPhos [4]

        Notes
        -----
        This method can be used to calculate the rate of mineralization for stable organic and inorganic phosphorus
        pools, as well as for the water-extractable organic phosphorus pool. The rates for stable organic,
        stable inorganic, and water-extractable organic phosphorus are 0.01, 0.0025, and 0.1 respectively.

        """
        return rate * min(temperature_factor, moisture_factor)

    @staticmethod
    def _determine_moisture_change(rainfall: float, current_moisture: float, current_mass: float, original_mass: float,
                                   temperature_factor: float) -> float:
        """This function determines the daily change in the moisture factor of the maure based on the current days
            precipitation conditions.

        Parameters
        ----------
        rainfall : float
            Amount of rainfall on the current day (mm)
        current_moisture : float
            Current value of the moisture factor (unitless)
        current_mass : float
            Current mass of dry matter content in the manure (kg)
        original_mass : float
            The mass of manure dry matter content originally applied to the field (kg)

        Returns
        -------
        float
            The change the moisture factor of the manure application on this day

        References
        ----------
        SurPhos [5, 6], pseudocode_soil [S.5.D.III.1]

        """
        if 1.0 <= rainfall <= 4.0:
            return 0.0

        if rainfall < 1.0:
            return (-1) * (-0.05 * (current_mass / original_mass) + 0.075) * temperature_factor

        return (-0.3 * current_moisture) + 0.27

    @staticmethod
    def _determine_rain_manure_dry_matter_ratio(rainfall: float, manure_dry_matter: float,
                                                manure_coverage: float) -> float:
        """Calculates the ratio of rainfall to manure dry matter currently on the field.

        Parameters
        ----------
        rainfall : float
            Amount of rainfall on the current day (mm)
        manure_dry_matter : float
            Current mass of manure dry matter on the field (kg)
        manure_coverage : float
            Area of the field covered by manure (ha)

        Returns
        -------
        float
            The ratio of rainfall to manure dry matter currently on the field (cubic cm per g)

        """
        rain_in_centimeters = rainfall * MILLIMETERS_TO_CENTIMETERS
        dry_matter_in_grams = manure_dry_matter * KILOGRAMS_TO_GRAMS
        coverage_in_square_centimeters = manure_coverage * HECTARES_TO_SQUARE_CENTIMETERS
        return (rain_in_centimeters / dry_matter_in_grams) * coverage_in_square_centimeters

    @staticmethod
    def _determine_water_extractable_inorganic_phosphorus_leached(manure_water_extractable_inorganic_phosphorus: float,
                                                                  rainfall_to_dry_manure_ratio: float,
                                                                  is_from_cow: bool) -> float:
        """Determines the amount of water extractable inorganic phosphorus leached by rainfall

        Parameters
        ----------
        manure_water_extractable_inorganic_phosphorus : float
            The amount of water extractable inorganic phosphorus from manure on the field (kg)
        rainfall_to_dry_manure_ratio : float
            The ratio of rainfall to manure dry matter on soil surface (cubic centimeters per gram)
        is_from_cow : float
            Is the water extractable inorganic phosphorus from cow manure (true / false)

        Returns
        -------
        float
            The amount of water extractable inorganic phosphorus leached from manure on the soil surface by rain on the
            given day (kg)

        References
        ----------
        SurPhos [9, 10], pseudocode_soil [S.5.D.I.3, II.1]

        Details
        -------
        Phosphorus leaching from cow manure is determined with a different set of constants than non-cow manure, which
        is why the is_from_cow parameter is necessary.

        """
        if is_from_cow:
            first_term = (1.2 * rainfall_to_dry_manure_ratio) / (rainfall_to_dry_manure_ratio + 73.1)
        else:
            first_term = (2.2 * rainfall_to_dry_manure_ratio) / (rainfall_to_dry_manure_ratio + 300.1)
        first_term = min(1.0, first_term)
        return max(0.0, first_term * manure_water_extractable_inorganic_phosphorus)

    @staticmethod
    def _determine_water_extractable_organic_phosphorus_leached(manure_water_extractable_organic_phosphorus: float,
                                                                rainfall_to_dry_manure_ratio: float,
                                                                is_from_cow: bool) -> float:
        """Determines the amount of water extractable organic phosphorus leached by rainfall

        Parameters
        ----------
        manure_water_extractable_organic_phosphorus : float
            The amount of water extractable inorganic phosphorus from manure on the field (kg)
        rainfall_to_dry_manure_ratio : float
            The ratio of rainfall to manure dry matter on soil surface (cubic centimeters per gram)
        is_from_cow : float
            Is the water extractable inorganic phosphorus from cow manure (true / false)

        Returns
        -------
        float
            The amount of water extractable inorganic phosphorus leached from manure on the soil surface by rain on the
            given day (kg)

        References
        ----------
        SurPhos [9, 10], pseudocode_soil [S.5.D.I.3, II.1]

        """
        result = Manure._determine_water_extractable_inorganic_phosphorus_leached(
            manure_water_extractable_organic_phosphorus, rainfall_to_dry_manure_ratio, is_from_cow)
        return result / 0.6

    @staticmethod
    def _determine_phosphorus_distribution_factor(rainfall: float, runoff: float) -> float:
        """Calculates a factor used to determine the concentration of Phosphorus dissolved in runoff, based on the ratio
            of rainfall to runoff

        Parameters
        ----------
        rainfall : float
            Amount of rainfall on the current day (mm)
        runoff : float
            Amount of runoff on the current day (mm)

        Returns
        -------
        float
            The ratio of rainfall to runoff adjusted for use in determining dissolved Phosphorus concentrations

        References
        ----------
        SurPhos [13], pseudocode_soil [S.5.D.II.2]

        """
        return (runoff / rainfall) ** 0.225

    @staticmethod
    def _determine_water_extractable_phosphorus_runoff_concentration(manure_leached: float, rainfall: float,
                                                                     field_size: float,
                                                                     distribution_factor: float) -> float:
        """Calculates the concentration of water extractable phosphorus in runoff on the current day.

        Parameters
        ----------
        manure_leached : float
            Mass of water extractable phosphorus leached from surface manure by rain on the current day (kg)
        rainfall : float
            Amount of rainfall on the current day (mm)
        field_size : float
            Size of the field (ha)
        distribution_factor : float
            Factor accounting for runoff to rainfall ratio on the current day (unitless)

        Returns
        -------
        float
            The concentration of water extractable phosphorus in runoff on the current day (milligrams per liter)

        """
        manure_leached_in_mg = manure_leached * KILOGRAMS_TO_MILLIGRAMS
        field_size_in_square_mm = field_size * HECTARES_TO_SQUARE_MILLIMETERS
        return manure_leached_in_mg * (1 / rainfall) * (1 / field_size_in_square_mm) * \
            (1 / CUBIC_MILLIMETERS_TO_LITERS) * distribution_factor

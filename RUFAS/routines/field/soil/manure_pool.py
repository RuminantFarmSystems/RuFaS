from typing import Any, Union, Dict
from math import exp, sqrt

from RUFAS.routines.field.soil.soil_data import SoilData
from RUFAS.routines.field.crop_and_soil_constants import (
    MILLIMETERS_TO_CENTIMETERS,
    KILOGRAMS_TO_GRAMS,
    KILOGRAMS_TO_MILLIGRAMS,
    HECTARES_TO_SQUARE_CENTIMETERS,
    HECTARES_TO_SQUARE_MILLIMETERS,
    CUBIC_MILLIMETERS_TO_LITERS,
    MILLIGRAMS_TO_KILOGRAMS,
)


class ManurePool:
    """
    Class that stores and tracks attributes of machine and grazing applied manure.

    manure_dry_mass : float, default 0
        The dry weight equivalent of manure mass on the field that was applied by machine or grazers (kg).
    manure_applied_mass : float, default 0
        The dry weight equivalent of the most recent application of manure applied by machine or grazers (kg).
    manure_field_coverage : float, default 0
        Fraction of the field that is covered by machine- or grazer-applied manure, between [0, 1] (unitless).
    manure_moisture_factor : float, default 0
        Fraction representing the current moisture level of the machine- or grazer-applied manure on the field, between
        [0, 0.9] (unitless).
    water_extractable_inorganic_phosphorus : float, default 0
        Amount of water extractable inorganic phosphorus on the field that was applied by machine or grazers (kg).
    water_extractable_organic_phosphorus : float, default 0
        Amount of water extractable organic phosphorus on the field that was applied by machine or grazers (kg).
    stable_inorganic_phosphorus : float, default 0
        Amount of stable inorganic phosphorus on the field that was applied by machine or grazers (kg).
    stable_organic_phosphorus : float, default 0
        Amount of stable organic phosphorus on the field that was applied by machine or grazers (kg).
    organic_phosphorus_runoff : float, default 0.0
        Amount of organic phosphorus from machine- or grazer-applied manure dissolved in and removed by runoff (kg).
    inorganic_phosphorus_runoff : float, default 0.0
        Amount of inorganic phosphorus from machine- or grazer-applied manure dissolved in and removed by runoff (kg).

    """

    def __init__(
        self,
        manure_dry_mass: float = 0.0,
        manure_applied_mass: float = 0.0,
        manure_field_coverage: float = 0.0,
        manure_moisture_factor: float = 0.0,
        water_extractable_inorganic_phosphorus: float = 0.0,
        water_extractable_organic_phosphorus: float = 0.0,
        stable_inorganic_phosphorus: float = 0.0,
        stable_organic_phosphorus: float = 0.0,
        organic_phosphorus_runoff: float = 0.0,
        inorganic_phosphorus_runoff: float = 0.0,
    ) -> None:
        self.manure_dry_mass = manure_dry_mass
        self.manure_applied_mass = manure_applied_mass
        self.manure_field_coverage = manure_field_coverage
        self.manure_moisture_factor = manure_moisture_factor
        self.water_extractable_inorganic_phosphorus = water_extractable_inorganic_phosphorus
        self.water_extractable_organic_phosphorus = water_extractable_organic_phosphorus
        self.stable_inorganic_phosphorus = stable_inorganic_phosphorus
        self.stable_organic_phosphorus = stable_organic_phosphorus
        self.organic_phosphorus_runoff = organic_phosphorus_runoff
        self.inorganic_phosphorus_runoff = inorganic_phosphorus_runoff

    def __eq__(self, other: Union["ManurePool", object]) -> Any:
        if not isinstance(other, ManurePool):
            return False
        return (
            self.manure_dry_mass == other.manure_dry_mass
            and self.manure_applied_mass == other.manure_applied_mass
            and self.manure_field_coverage == other.manure_field_coverage
            and self.manure_moisture_factor == other.manure_moisture_factor
            and self.water_extractable_inorganic_phosphorus == other.water_extractable_inorganic_phosphorus
            and self.water_extractable_organic_phosphorus == other.water_extractable_organic_phosphorus
            and self.stable_inorganic_phosphorus == other.stable_inorganic_phosphorus
            and self.stable_organic_phosphorus == other.stable_organic_phosphorus
            and self.organic_phosphorus_runoff == other.organic_phosphorus_runoff
            and self.inorganic_phosphorus_runoff == other.inorganic_phosphorus_runoff
        )

    def determine_decomposed_surface_manure(self, temperature_factor: float) -> tuple[float, float]:
        """
        This method calculates how much manure in both the machine and grazer-applied pools decompose on a given day,
        and how much the field coverage changes as a result.

        Parameters
        ----------
        temperature_factor : float
            The temperature factor on the current day (unitless).

        Returns
        -------
        Tuple[float, float]
            decomposed_manure_mass_change: change in the mass of applied manure on the field surface
                decomposed on this day (kg).
            decomposed_manure_coverage_change: change in field coverage of applied manure on the field
                surface (unitless).
        """
        manure_dry_matter_decomposition_rate = max(
            0.0, self._determine_dry_matter_decomposition_rate(temperature_factor)
        )
        (
            decomposed_manure_mass_change,
            decomposed_manure_coverage_change,
        ) = (0, 0)
        if self.manure_dry_mass > 0 and self.manure_field_coverage > 0:
            decomposed_manure_mass_change = min(
                (self.manure_dry_mass * manure_dry_matter_decomposition_rate),
                self.manure_dry_mass,
            )
            decomposed_manure_coverage_change = min(
                (decomposed_manure_mass_change / self.manure_dry_mass)
                * self.manure_field_coverage,
                self.manure_field_coverage,
            )

        return decomposed_manure_mass_change, decomposed_manure_coverage_change

    def _determine_assimilated_surface_manure(self,
                                              temperature_factor: float,
                                              field_size: float) -> tuple[float, float]:
        """
        Determines how much manure is assimilated into the soil profile and how much the manure coverage is reduced
        by on the current day.

        Parameters
        ----------
        temperature_factor : float
            The temperature factor on the current day (unitless).
        field_size : float
            The area of the field (ha).

        Returns
        -------
        Tuple[float, float]
            assimilated_manure: Amount of manure that is assimilated on a given day (kg).
            manure_coverage: Amount of decrease in the fraction of field covered by manure on a given day (unitless).

        """
        assimilated_manure, manure_coverage = 0, 0
        if self.manure_dry_mass > 0 and self.manure_field_coverage > 0:
            manure_cover_area = self.manure_field_coverage * field_size
            assimilated_manure = max(
                0.0,
                self._determine_dry_manure_matter_assimilation(
                    self.manure_moisture_factor,
                    temperature_factor,
                    manure_cover_area,
                    False
                )
            )
            assimilated_manure = min(self.manure_dry_mass, assimilated_manure)
            manure_coverage = max(
                0.0,
                (assimilated_manure / self.manure_dry_mass)
                * self.manure_field_coverage,
            )
            manure_coverage = min(manure_coverage, self.manure_field_coverage)
        return assimilated_manure, manure_coverage

    @staticmethod
    def _determine_temperature_factor(mean_air_temperature: float) -> float:
        """
        Calculates the temperature factor for the current day

        Parameters
        ----------
        mean_air_temperature : float
            The average air temperature of the current day (degrees Celsius).

        Returns
        -------
        float
            The temperature factor on the current day (unitless).

        References
        ----------
        SurPhos [2], pseudocode_soil [S.5.D.I.1]

        """
        calculated_temperature_factor = (
                                            (2 * (32 ** 2) * (mean_air_temperature ** 2)) - (mean_air_temperature ** 4)
                                        ) / (32 ** 4)
        return min(1.0, max(0.0, calculated_temperature_factor))

    @staticmethod
    def _determine_dry_matter_decomposition_rate(temperature_factor: float) -> float:
        """
        Calculates the rate of manure dry matter decomposition on the current day.

        Parameters
        ----------
        temperature_factor : float
            The temperature factor on the current day (unitless).

        Returns
        -------
        float
            The rate of manure dry matter decomposition on the current day (unitless).

        References
        ----------
        SurPhos [1], pseudocode_soil [S.5.D.III.4]

        """
        return 0.003 * (temperature_factor ** 0.5)

    @staticmethod
    def _determine_dry_manure_matter_assimilation(
        moisture_factor: float,
        temperature_factor: float,
        manure_cover_area: float,
        is_dung: bool,
    ) -> float:
        """
        Calculates the mass of dry manure matter applied by machine assimilated into the soil that day.

        Parameters
        ----------
        moisture_factor : float
            Manure moisture factor, in range [0.0, 1.0] (unitless).
        temperature_factor : float
            The temperature factor on the current day (unitless).
        manure_cover_area : float
            Area of the field covered by manure (ha).
        is_dung : bool
            Was the manure being assimilated applied by animals grazing in the field (true / false).

        Returns
        -------
        float
            The amount of manure dry matter that is assimilated into the soil by macroinvertebrates (bioturbation) on
            the current day (kg).

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
    def _determine_moisture_change(
        rainfall: float,
        current_moisture: float,
        current_mass: float,
        original_mass: float,
        temperature_factor: float,
    ) -> float:
        """
        This function determines the daily change in the moisture factor of the maure based on the current days
        precipitation conditions.

        Parameters
        ----------
        rainfall : float
            Amount of rainfall on the current day (mm).
        current_moisture : float
            Current value of the moisture factor (unitless).
        current_mass : float
            Current mass of dry matter content in the manure (kg).
        original_mass : float
            The mass of manure dry matter content originally applied to the field (kg).

        Returns
        -------
        float
            The change the moisture factor of the manure application on this day.

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
    def _determine_rain_manure_dry_matter_ratio(
        rainfall: float, manure_dry_matter: float, manure_coverage: float
    ) -> float:
        """
        Calculates the ratio of rainfall to manure dry matter currently on the field.

        Parameters
        ----------
        rainfall : float
            Amount of rainfall on the current day (mm).
        manure_dry_matter : float
            Current mass of manure dry matter on the field (kg).
        manure_coverage : float
            Area of the field covered by manure (ha).

        Returns
        -------
        float
            The ratio of rainfall to manure dry matter currently on the field (cubic cm per g).

        References
        ----------
        SurPhos Theoretical Documentation [11]

        """
        rain_in_centimeters = rainfall * MILLIMETERS_TO_CENTIMETERS
        dry_matter_in_grams = manure_dry_matter * KILOGRAMS_TO_GRAMS
        coverage_in_square_centimeters = manure_coverage * HECTARES_TO_SQUARE_CENTIMETERS
        return (rain_in_centimeters / dry_matter_in_grams) * coverage_in_square_centimeters

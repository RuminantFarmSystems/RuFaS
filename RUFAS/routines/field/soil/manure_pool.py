from math import exp, sqrt
from typing import Any, Union

from RUFAS.general_constants import GeneralConstants


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
    annual_decomposed_manure : float, default 0.0
        Amount of annual manure decomposed/mineralized (kg).

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
        annual_runoff_manure_inorganic_phosphorus: float = 0.0,
        annual_runoff_manure_organic_phosphorus: float = 0.0,
        annual_decomposed_manure: float = 0.0,
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
        self.annual_runoff_manure_inorganic_phosphorus = annual_runoff_manure_inorganic_phosphorus
        self.annual_runoff_manure_organic_phosphorus = annual_runoff_manure_organic_phosphorus
        self.annual_decomposed_manure = annual_decomposed_manure

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
            and self.annual_runoff_manure_organic_phosphorus == other.annual_runoff_manure_organic_phosphorus
            and self.annual_runoff_manure_inorganic_phosphorus == other.annual_runoff_manure_inorganic_phosphorus
        )

    def daily_manure_update(
        self,
        rainfall: float,
        field_size: float,
        mean_air_temperature: float,
    ) -> float:
        """
        This method conducts daily operations on manure including decomposition, assimilation and returns the total
        assimilation.

        Parameters
        ----------
        rainfall : float
            The amount of rainfall on the current day (mm).
        field_size : float
            The size of the field (ha).
        mean_air_temperature : float
            Mean air temperature on the current day (degrees C).

        return
        ------
        float
            The total amount of assimilated phosphorus (kg).
        """
        temperature_factor = self._determine_temperature_factor(mean_air_temperature)
        if rainfall < 1 or rainfall > 4:
            self.adjust_manure_moisture_factor(rainfall, temperature_factor)

        decomposed_mass, decomposed_coverage = self.determine_decomposed_surface_manure(temperature_factor)

        mineralized_stable_organic = self.determine_mineralized_surface_phosphorus(
            self.stable_organic_phosphorus,
            0.01,
            temperature_factor,
            self.manure_moisture_factor,
        )

        self.stable_organic_phosphorus = max(0.0, self.stable_organic_phosphorus - mineralized_stable_organic)

        mineralized_stable_inorganic = self.determine_mineralized_surface_phosphorus(
            self.stable_inorganic_phosphorus,
            0.0025,
            temperature_factor,
            self.manure_moisture_factor,
        )

        self.stable_inorganic_phosphorus = max(0.0, self.stable_inorganic_phosphorus - mineralized_stable_inorganic)

        mineralized_water_extractable_organic = self.determine_mineralized_surface_phosphorus(
            self.water_extractable_organic_phosphorus,
            0.1,
            temperature_factor,
            self.manure_moisture_factor,
        )

        self.water_extractable_organic_phosphorus = max(
            0.0, self.water_extractable_organic_phosphorus - mineralized_water_extractable_organic
        )

        self.annual_decomposed_manure += (
            mineralized_water_extractable_organic + mineralized_stable_organic + mineralized_stable_inorganic
        )

        assimilated_mass, assimilated_coverage = self.determine_assimilated_surface_manure(
            temperature_factor, field_size
        )
        if self.manure_dry_mass > 0:
            assimilation_ratio = assimilated_mass / self.manure_dry_mass
        else:
            assimilation_ratio = 0

        assimilated_stable_organic = self.determine_assimilated_phosphorus_amount(
            assimilation_ratio, self.stable_organic_phosphorus
        )
        assimilated_stable_inorganic = self.determine_assimilated_phosphorus_amount(
            assimilation_ratio, self.stable_inorganic_phosphorus
        )
        assimilated_water_extractable_organic = self.determine_assimilated_phosphorus_amount(
            assimilation_ratio, self.water_extractable_organic_phosphorus
        )
        assimilated_water_extractable_inorganic = self.determine_assimilated_phosphorus_amount(
            assimilation_ratio, self.water_extractable_inorganic_phosphorus
        )

        self.manure_dry_mass = max(0.0, self.manure_dry_mass - assimilated_mass - decomposed_mass)

        self.manure_field_coverage = max(
            0.0,
            self.manure_field_coverage - assimilated_coverage - decomposed_coverage,
        )

        self.stable_organic_phosphorus = max(
            0.0,
            self.stable_organic_phosphorus - assimilated_stable_organic,
        )

        self.stable_inorganic_phosphorus = max(
            0.0,
            self.stable_inorganic_phosphorus - assimilated_stable_inorganic,
        )

        self.water_extractable_organic_phosphorus = max(
            0.0, self.water_extractable_organic_phosphorus - assimilated_water_extractable_organic
        )

        self.water_extractable_inorganic_phosphorus = max(
            0.0,
            self.water_extractable_inorganic_phosphorus - assimilated_water_extractable_inorganic,
        )

        self.water_extractable_inorganic_phosphorus += (
            mineralized_water_extractable_organic + (0.75 * mineralized_stable_organic) + mineralized_stable_inorganic
        )

        self.water_extractable_organic_phosphorus += 0.25 * mineralized_stable_organic

        return (
            assimilated_stable_organic
            + assimilated_stable_inorganic
            + assimilated_water_extractable_organic
            + assimilated_water_extractable_inorganic
        )

    def runoff_reset(self):
        """Helper method to reset phosphorus runoff"""
        self.organic_phosphorus_runoff = 0.0
        self.inorganic_phosphorus_runoff = 0.0

    def leach_phosphorus_pools(self, rainfall: float, runoff: float, field_size: float) -> tuple[float, float]:
        """
        This method handles all calls to the methods that determine how much phosphorus is leached from manure, how
        that leached phosphorus is distributed.

        Parameters
        ----------
        rainfall : float
            The amount of rainfall on the current day (mm).
        runoff : float
            The amount of runoff from rainfall on the current day (mm).
        field_size : float
            The size of the field (ha).

        """
        organic_results = self._determine_phosphorus_leached_from_surface(
            rainfall,
            runoff,
            field_size,
            self.manure_dry_mass,
            self.manure_field_coverage,
            self.water_extractable_organic_phosphorus,
            True,
        )
        self.water_extractable_organic_phosphorus = organic_results["new_phosphorus_pool_amount"]
        self.organic_phosphorus_runoff = organic_results["runoff_phosphorus"]
        self.annual_runoff_manure_organic_phosphorus += organic_results["runoff_phosphorus"]

        inorganic_results = self._determine_phosphorus_leached_from_surface(
            rainfall,
            runoff,
            field_size,
            self.manure_dry_mass,
            self.manure_field_coverage,
            self.water_extractable_inorganic_phosphorus,
            False,
        )
        self.water_extractable_inorganic_phosphorus = inorganic_results["new_phosphorus_pool_amount"]
        self.inorganic_phosphorus_runoff = inorganic_results["runoff_phosphorus"]
        self.annual_runoff_manure_inorganic_phosphorus += inorganic_results["runoff_phosphorus"]
        return organic_results["infiltrated_phosphorus"], inorganic_results["infiltrated_phosphorus"]

    def adjust_manure_moisture_factor(self, rainfall: float, temperature_factor: float) -> None:
        """
        Adjusts the moisture factor of manure on the soil surface based on the current day's precipitation level.

        Parameters
        ----------
        rainfall : float
            The amount of rainfall on the current day (mm).
        temperature_factor : float
            The temperature factor on the current day (unitless).

        """
        if self.manure_dry_mass > 0 and self.manure_field_coverage > 0:
            change_in_machine_manure_moisture = self._determine_moisture_change(
                rainfall,
                self.manure_moisture_factor,
                self.manure_dry_mass,
                self.manure_applied_mass,
                temperature_factor,
            )
            self.manure_moisture_factor += change_in_machine_manure_moisture
            self.manure_moisture_factor = min(0.9, max(self.manure_moisture_factor, 0.0))

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
                (decomposed_manure_mass_change / self.manure_dry_mass) * self.manure_field_coverage,
                self.manure_field_coverage,
            )

        return decomposed_manure_mass_change, decomposed_manure_coverage_change

    def determine_assimilated_surface_manure(self, temperature_factor: float, field_size: float) -> tuple[float, float]:
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
        tuple[float, float]
            assimilated_manure: Amount of manure that is assimilated on a given day (kg).
            manure_coverage: Amount of decrease in the fraction of field covered by manure on a given day (unitless).

        """
        assimilated_manure, manure_coverage = 0, 0
        if self.manure_dry_mass > 0 and self.manure_field_coverage > 0:
            manure_cover_area = self.manure_field_coverage * field_size
            assimilated_manure = max(
                0.0,
                self._determine_dry_manure_matter_assimilation(
                    self.manure_moisture_factor, temperature_factor, manure_cover_area, False
                ),
            )
            assimilated_manure = min(self.manure_dry_mass, assimilated_manure)
            manure_coverage = max(
                0.0,
                (assimilated_manure / self.manure_dry_mass) * self.manure_field_coverage,
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
            (2 * (32**2) * (mean_air_temperature**2)) - (mean_air_temperature**4)
        ) / (32**4)
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
        return 0.003 * (temperature_factor**0.5)

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
            temperature_term = temperature_factor**0.1
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
        rain_in_centimeters = rainfall * GeneralConstants.MM_TO_CM
        dry_matter_in_grams = manure_dry_matter * GeneralConstants.KG_TO_GRAMS
        coverage_in_square_centimeters = manure_coverage * GeneralConstants.HECTARES_TO_SQUARE_CENTIMETERS
        return (rain_in_centimeters / dry_matter_in_grams) * coverage_in_square_centimeters

    @staticmethod
    def _determine_phosphorus_leached_from_surface(
        rainfall: float,
        runoff: float,
        field_size: float,
        manure_dry_mass: float,
        field_coverage: float,
        water_extractable_phosphorus: float,
        is_organic: bool,
    ) -> dict[str, float]:
        """
        This method determines how much phosphorus is leached from the given pool, how that phosphorus is distributed
        between runoff and soil infiltration, and how much phosphorus remains in the given pool.

        Parameters
        ----------
        rainfall : float
            The amount of rainfall on the current day (mm).
        runoff : float
            The amount of runoff from rainfall on the current day (mm).
        field_size : float
            Area of the field (ha).
        manure_dry_mass : float
            Dry-weight equivalent of manure on the field (kg).
        field_coverage : float
            Percent of the field covered by manure, in range [0.0, 1.0] (unitless).
        water_extractable_phosphorus : float
            The mass of the water extractable phosphorus pool that is being leached from (kg).
        is_organic : bool
            Is the phosphorus being leached organic (True / False).

        Returns
        -------
        dict (keys listed below)
            new_phosphorus_pool_amount: amount of phosphorus in the pool after leaching from it (kg).
            infiltrated_phosphorus: amount of phosphorus that infiltrates into the soil profile (kg).
            runoff_phosphorus: amount of phosphorus that leaves the field dissolved in runoff (kg).

        Notes
        -----
        This method follows the steps outlined for how to calculate phosphorus lost from a field's surface as outlined
        by the section with the header "Phosphorus Leaching from Manure by Rain" (page 8). Generally, the steps are
            - Calculate the ratios of rainfall to manure mass and rainfall to runoff on the given day.
            - Calculate the amounts of water extractable phosphorus lost by the surface manure pools on a given day.
            - Calculate how much of the leached phosphorus runs off the field and how much infiltrates the soil based on
                the ratios calculated above.
            - Determine how much phosphorus is remains in the surface pool after leaching.
            - Return all the above amounts of phosphorus (lost to runoff, infiltrated soil, still on field surface).

        """
        area_covered_by_manure = field_coverage * field_size
        rain_manure_dry_matter_ratio = ManurePool._determine_rain_manure_dry_matter_ratio(
            rainfall, manure_dry_mass, area_covered_by_manure
        )

        distribution_factor = ManurePool._determine_phosphorus_distribution_factor(rainfall, runoff)

        if is_organic:
            water_extractable_phosphorus_leached = ManurePool._determine_water_extractable_phosphorus_leached(
                water_extractable_phosphorus, rain_manure_dry_matter_ratio, True, True
            )
        else:
            water_extractable_phosphorus_leached = ManurePool._determine_water_extractable_phosphorus_leached(
                water_extractable_phosphorus, rain_manure_dry_matter_ratio, True, False
            )

        water_extractable_phosphorus_leached = min(water_extractable_phosphorus, water_extractable_phosphorus_leached)

        runoff_dissolved_phosphorus_concentration = (
            ManurePool._determine_water_extractable_phosphorus_runoff_concentration(
                water_extractable_phosphorus_leached,
                rainfall,
                field_size,
                distribution_factor,
            )
        )

        runoff_in_liters = (
            runoff
            * (field_size * GeneralConstants.HECTARES_TO_SQUARE_MILLIMETERS)
            * GeneralConstants.CUBIC_MILLIMETERS_TO_LITERS
        )

        phosphorus_lost_to_runoff_in_kg = (
            runoff_dissolved_phosphorus_concentration * runoff_in_liters
        ) * GeneralConstants.MILLIGRAMS_TO_KG

        infiltrated_phosphorus = max(0, water_extractable_phosphorus_leached - phosphorus_lost_to_runoff_in_kg)

        new_phosphorus_pool_amount = water_extractable_phosphorus - water_extractable_phosphorus_leached
        return_dict = {
            "new_phosphorus_pool_amount": new_phosphorus_pool_amount,
            "infiltrated_phosphorus": infiltrated_phosphorus,
            "runoff_phosphorus": phosphorus_lost_to_runoff_in_kg,
        }
        return return_dict

    @staticmethod
    def determine_mineralized_surface_phosphorus(
        phosphorus_amount: float,
        rate: float,
        temperature_factor: float,
        moisture_factor: float,
    ) -> float:
        """
        Calculates the amount of phosphorus that mineralizes into water-extractable inorganic phosphorus on the
        current day from the given pool.

        Parameters
        ----------
        phosphorus_amount : float
            The amount of phosphorus in the pool that is being mineralized (kg).
        rate : float
            The rate factor for the type of phosphorus being mineralized (unitless).
        temperature_factor : float
            The temperature factor on the current day (unitless).
        moisture_factor : float
            The moisture factor of the given manure pool on the current day (unitless).

        Returns
        -------
        float
            The amount of phosphorus that is mineralized from that pool that is passed (kg).

        References
        ----------
        SurPhos theoretical documentation eqn. [4]

        Notes
        -----
        As defined in the paragraph on page 6 of the SurPhos theoretical documentation underneath eqn. [4], the rates
        for stable organic Phosphorus, stable inorganic phosphorus, and water-extractable organic phosphorus are 0.01,
        0.0025, and 0.1, respectively.

        """
        mineralization_rate = rate * min(temperature_factor, moisture_factor)
        return min(phosphorus_amount, max(0.0, phosphorus_amount * mineralization_rate))

    @staticmethod
    def determine_assimilated_phosphorus_amount(assimilation_ratio: float, phosphorus_amount: float) -> float:
        """
        Calculates the amount of phosphorus that is removed through assimilation on a given day.

        Parameters
        ----------
        assimilation_ratio : float
            Ratio of manure mass assimilated to amount present before assimilation (unitless).
        phosphorus_amount : float
            The amount of phosphorus in the pool being removed from (kg).

        Returns
        -------
        float
            The amount of phosphorus removed from the pool (kg).

        """
        return min(phosphorus_amount, max(0.0, assimilation_ratio * phosphorus_amount))

    @staticmethod
    def _determine_phosphorus_distribution_factor(rainfall: float, runoff: float) -> float:
        """
        Calculates a factor used to determine the concentration of Phosphorus dissolved in runoff, based on the ratio
        of rainfall to runoff.

        Parameters
        ----------
        rainfall : float
            Amount of rainfall on the current day (mm).
        runoff : float
            The amount of runoff from rainfall on the current day (mm).

        Returns
        -------
        float
            The ratio of rainfall to runoff adjusted for use in determining dissolved Phosphorus concentrations.

        References
        ----------
        SurPhos [13], pseudocode_soil [S.5.D.II.2]

        """
        return (runoff / rainfall) ** 0.225

    @staticmethod
    def _determine_water_extractable_phosphorus_leached(
        manure_water_extractable_phosphorus: float,
        rainfall_to_dry_manure_ratio: float,
        is_from_cow: bool,
        organic_phosphorus: bool,
    ) -> float:
        """
        Determines the amount of water extractable organic or inorganic phosphorus leached by rainfall.

        Parameters
        ----------
        manure_water_extractable_phosphorus : float
            The amount of water extractable phosphorus from manure on the field (kg).
        rainfall_to_dry_manure_ratio : float
            The ratio of rainfall to manure dry matter on soil surface (cubic centimeters per gram).
        is_from_cow : float
            Is the water extractable inorganic phosphorus from cow manure (true / false).
        organic_phosphorus: bool
            True for organic phosphorus calculation, False for inorganic phosphorus.

        Returns
        -------
        float
            The amount of water extractable phosphorus leached from manure on the soil surface by rain on the given
            day (kg).

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
        result = max(0.0, first_term * manure_water_extractable_phosphorus)
        return result if not organic_phosphorus else result / 0.6

    @staticmethod
    def _determine_water_extractable_phosphorus_runoff_concentration(
        manure_leached: float,
        rainfall: float,
        field_size: float,
        distribution_factor: float,
    ) -> float:
        """
        Calculates the concentration of water extractable phosphorus in runoff on the current day.

        Parameters
        ----------
        manure_leached : float
            Mass of water extractable phosphorus leached from surface manure by rain on the current day (kg).
        rainfall : float
            Amount of rainfall on the current day (mm).
        field_size : float
            Size of the field (ha).
        distribution_factor : float
            Factor accounting for runoff to rainfall ratio on the current day (unitless).

        Returns
        -------
        float
            The concentration of water extractable phosphorus in runoff on the current day (milligrams per liter).

        """
        manure_leached_in_mg = manure_leached * GeneralConstants.KG_TO_MILLIGRAMS
        field_size_in_square_mm = field_size * GeneralConstants.HECTARES_TO_SQUARE_MILLIMETERS
        return (
            manure_leached_in_mg
            * (1 / rainfall)
            * (1 / field_size_in_square_mm)
            * (1 / GeneralConstants.CUBIC_MILLIMETERS_TO_LITERS)
            * distribution_factor
        )

    def determine_phosphorus_leach(self) -> bool:
        """
        Determine if phosphorus leaching operations should run.

        Returns
        -------
        bool
            The status to determine if phosphorus leaching should run.
        """
        return self.manure_dry_mass > 0 and self.manure_field_coverage > 0

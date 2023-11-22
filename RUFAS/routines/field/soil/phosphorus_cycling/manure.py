from typing import Optional, Dict
from math import exp, sqrt

from RUFAS.routines.field.soil.soil_data import SoilData
from RUFAS.routines.field.crop_and_soil_constants import MILLIMETERS_TO_CENTIMETERS, KILOGRAMS_TO_GRAMS, \
    KILOGRAMS_TO_MILLIGRAMS, HECTARES_TO_SQUARE_CENTIMETERS, HECTARES_TO_SQUARE_MILLIMETERS, \
    CUBIC_MILLIMETERS_TO_LITERS, MILLIGRAMS_TO_KILOGRAMS

"""
This module adds and tracks manure phosphorus dynamics based on the SurPhos model.
"""


class Manure:

    def __init__(self, soil_data: Optional[SoilData], field_size: Optional[float] = None):
        """This method initializes the SoilData object that this module will work with, or create one if none provided.

        Parameters
        ----------
        soil_data : SoilData, optional
            The SoilData object used by this module to track manure phosphorus activity, creates new one if one is not
            provided.
        field_size : float, optional
            Used to initialize a SoilData object for this module to work with, if a pre-configured SoilData object is
            not provided (ha)

        """
        self.data = soil_data or SoilData(field_size=field_size)

    def daily_manure_update(self, rainfall: float, runoff: float, field_size: float,
                            mean_air_temperature: float) -> None:
        """This method conducts daily operations on manure including decomposition, assimilation into soil, etc.

        Parameters
        ----------
        rainfall : float
            The amount of rainfall on the current day (mm)
        runoff : float
            The amount of runoff from rainfall on the current day (mm)
        field_size : float
            The size of the field (ha)
        mean_air_temperature : float
            Mean air temperature on the current day (degrees C)

        Notes
        -----
        This method orchestrates the three major processes (and one more minor process) that act on manure on the manure
        on the surface of the field. The three major processes are leaching, decomposition, and assimilation. The minor
        process is the adjustment of the manure's moisture factor. Leaching is conducted first, then the adjustment of
        the moisture factors. Decomposition and assimilation occur simultaneously.

        """
        self.data.machine_organic_phosphorus_runoff = 0.0
        self.data.machine_inorganic_phosphorus_runoff = 0.0
        self.data.grazing_organic_phosphorus_runoff = 0.0
        self.data.grazing_inorganic_phosphorus_runoff = 0.0

        if rainfall > 0:
            self._leach_and_update_phosphorus_pools(rainfall, runoff, field_size)

        temperature_factor = self._determine_temperature_factor(mean_air_temperature)

        if rainfall < 1 or rainfall > 4:
            self._adjust_manure_moisture_factor(rainfall, temperature_factor)

        # Calculate manure decomposition on soil surface
        decomposition_changes = self._determine_decomposed_surface_manure(temperature_factor)
        decomposed_machine_mass = decomposition_changes["decomposed_machine_manure_mass_change"]
        decomposed_machine_coverage = decomposition_changes["decomposed_machine_manure_coverage_change"]
        decomposed_grazing_mass = decomposition_changes["decomposed_grazing_manure_mass_change"]
        decomposed_grazing_coverage = decomposition_changes["decomposed_grazing_manure_coverage_change"]

        # Calculate phosphorus mineralization between pools
        mineralized_machine_stable_organic = self._determine_mineralized_surface_phosphorus(
            self.data.machine_stable_organic_phosphorus, 0.01, temperature_factor,
            self.data.machine_manure_moisture_factor)
        mineralized_machine_stable_inorganic = self._determine_mineralized_surface_phosphorus(
            self.data.machine_stable_inorganic_phosphorus, 0.0025, temperature_factor,
            self.data.machine_manure_moisture_factor)
        mineralized_machine_water_extractable_organic = self._determine_mineralized_surface_phosphorus(
            self.data.machine_water_extractable_organic_phosphorus, 0.1, temperature_factor,
            self.data.machine_manure_moisture_factor)

        mineralized_grazing_stable_organic = self._determine_mineralized_surface_phosphorus(
            self.data.grazing_stable_organic_phosphorus, 0.01, temperature_factor,
            self.data.grazing_manure_moisture_factor)
        mineralized_grazing_stable_inorganic = self._determine_mineralized_surface_phosphorus(
            self.data.grazing_stable_inorganic_phosphorus, 0.0025, temperature_factor,
            self.data.grazing_manure_moisture_factor)
        mineralized_grazing_water_extractable_organic = self._determine_mineralized_surface_phosphorus(
            self.data.grazing_water_extractable_organic_phosphorus, 0.1, temperature_factor,
            self.data.grazing_manure_moisture_factor)

        # Calculate manure assimilation from soil surface into profile
        assimilated_manure_changes = self._determine_assimilated_surface_manure(temperature_factor, field_size)
        assimilated_machine_mass = assimilated_manure_changes["assimilated_machine_manure"]
        assimilated_machine_coverage = assimilated_manure_changes["machine_manure_coverage"]
        assimilated_grazing_mass = assimilated_manure_changes["assimilated_grazing_manure"]
        assimilated_grazing_coverage = assimilated_manure_changes["grazing_manure_coverage"]

        # Calculate amounts of phosphorus assimilated into the soil
        if self.data.machine_manure_dry_mass > 0:
            machine_assimilation_ratio = assimilated_machine_mass / self.data.machine_manure_dry_mass
        else:
            machine_assimilation_ratio = 0
        assimilated_machine_stable_organic = self._determine_assimilated_phosphorus_amount(
            machine_assimilation_ratio, self.data.machine_stable_organic_phosphorus)
        assimilated_machine_stable_inorganic = self._determine_assimilated_phosphorus_amount(
            machine_assimilation_ratio, self.data.machine_stable_inorganic_phosphorus)
        assimilated_machine_water_extractable_organic = self._determine_assimilated_phosphorus_amount(
            machine_assimilation_ratio, self.data.machine_water_extractable_organic_phosphorus)
        assimilated_machine_water_extractable_inorganic = self._determine_assimilated_phosphorus_amount(
            machine_assimilation_ratio, self.data.machine_water_extractable_inorganic_phosphorus)

        if self.data.grazing_manure_dry_mass > 0:
            grazing_assimilation_ratio = assimilated_grazing_mass / self.data.grazing_manure_dry_mass
        else:
            grazing_assimilation_ratio = 0
        assimilated_grazing_stable_organic = self._determine_assimilated_phosphorus_amount(
            grazing_assimilation_ratio, self.data.grazing_stable_organic_phosphorus)
        assimilated_grazing_stable_inorganic = self._determine_assimilated_phosphorus_amount(
            grazing_assimilation_ratio, self.data.grazing_stable_inorganic_phosphorus)
        assimilated_grazing_water_extractable_organic = self._determine_assimilated_phosphorus_amount(
            grazing_assimilation_ratio, self.data.grazing_water_extractable_organic_phosphorus)
        assimilated_grazing_water_extractable_inorganic = self._determine_assimilated_phosphorus_amount(
            grazing_assimilation_ratio, self.data.grazing_water_extractable_inorganic_phosphorus)

        # Set machine attributes
        self.data.machine_manure_dry_mass = \
            max(0.0, self.data.machine_manure_dry_mass - assimilated_machine_mass - decomposed_machine_mass)
        self.data.machine_manure_field_coverage = \
            max(0.0,
                self.data.machine_manure_field_coverage - assimilated_machine_coverage - decomposed_machine_coverage)
        self.data.machine_stable_organic_phosphorus = \
            max(0.0, self.data.machine_stable_organic_phosphorus - assimilated_machine_stable_organic -
                mineralized_machine_stable_organic)
        self.data.machine_stable_inorganic_phosphorus = \
            max(0.0, self.data.machine_stable_inorganic_phosphorus - assimilated_machine_stable_inorganic -
                mineralized_machine_stable_inorganic)
        self.data.machine_water_extractable_organic_phosphorus = \
            max(0.0, self.data.machine_water_extractable_organic_phosphorus -
                assimilated_machine_water_extractable_organic - mineralized_machine_water_extractable_organic)
        self.data.machine_water_extractable_inorganic_phosphorus = \
            max(0.0, self.data.machine_water_extractable_inorganic_phosphorus -
                assimilated_machine_water_extractable_inorganic)

        self.data.machine_water_extractable_inorganic_phosphorus += mineralized_machine_water_extractable_organic + \
            (0.75 * mineralized_machine_stable_organic) + mineralized_machine_stable_inorganic
        self.data.machine_water_extractable_organic_phosphorus += (0.25 * mineralized_machine_stable_organic)

        # Set grazing attributes
        self.data.grazing_manure_dry_mass = \
            max(0.0, self.data.grazing_manure_dry_mass - assimilated_grazing_mass - decomposed_grazing_mass)
        self.data.grazing_manure_field_coverage = \
            max(0.0,
                self.data.grazing_manure_field_coverage - assimilated_grazing_coverage - decomposed_grazing_coverage)
        self.data.grazing_stable_organic_phosphorus = \
            max(0.0, self.data.grazing_stable_organic_phosphorus - assimilated_grazing_stable_organic -
                mineralized_grazing_stable_organic)
        self.data.grazing_stable_inorganic_phosphorus = \
            max(0.0, self.data.grazing_stable_inorganic_phosphorus - assimilated_grazing_stable_inorganic -
                mineralized_grazing_stable_inorganic)
        self.data.grazing_water_extractable_organic_phosphorus = \
            max(0.0, self.data.grazing_water_extractable_organic_phosphorus -
                assimilated_grazing_water_extractable_organic - mineralized_grazing_water_extractable_organic)
        self.data.grazing_water_extractable_inorganic_phosphorus = \
            max(0.0, self.data.grazing_water_extractable_inorganic_phosphorus -
                assimilated_grazing_water_extractable_inorganic)

        self.data.grazing_water_extractable_inorganic_phosphorus += mineralized_grazing_water_extractable_organic + \
            (0.75 * mineralized_grazing_stable_organic) + mineralized_grazing_stable_inorganic
        self.data.grazing_water_extractable_organic_phosphorus += (0.25 * mineralized_grazing_stable_organic)

        # Add assimilated phosphorus to the soil profile
        total_assimilated_phosphorus = assimilated_machine_stable_organic + assimilated_machine_stable_inorganic + \
            assimilated_machine_water_extractable_organic + assimilated_machine_water_extractable_inorganic + \
            assimilated_grazing_stable_organic + assimilated_grazing_stable_inorganic + \
            assimilated_grazing_water_extractable_organic + assimilated_grazing_water_extractable_inorganic
        self._add_infiltrated_phosphorus_to_soil(total_assimilated_phosphorus, field_size)

    def _leach_and_update_phosphorus_pools(self, rainfall: float, runoff: float, field_size: float) -> None:
        """This method handles all calls to the methods that determine how much phosphorus is leached from manure, how
            that leached phosphorus is distributed, and updates the phosphorus pools based on those values.

        Parameters
        ----------
        rainfall : float
            The amount of rainfall on the current day (mm)
        runoff : float
            The amount of runoff from rainfall on the current day (mm)
        field_size : float
            The size of the field (ha)

        """
        if self.data.machine_manure_dry_mass > 0 and self.data.machine_manure_field_coverage > 0:
            machine_organic_results = \
                self._determine_phosphorus_leached_from_surface(rainfall, runoff, field_size,
                                                                self.data.machine_manure_dry_mass,
                                                                self.data.machine_manure_field_coverage,
                                                                self.data.machine_water_extractable_organic_phosphorus,
                                                                True)
            self.data.machine_water_extractable_organic_phosphorus = \
                machine_organic_results["new_phosphorus_pool_amount"]
            self.data.machine_organic_phosphorus_runoff = machine_organic_results["runoff_phosphorus"]
            self.data.annual_runoff_machine_manure_organic_phosphorus += machine_organic_results["runoff_phosphorus"]
            self._add_infiltrated_phosphorus_to_soil(machine_organic_results["infiltrated_phosphorus"], field_size)

            machine_inorganic_results = \
                self._determine_phosphorus_leached_from_surface(
                    rainfall, runoff, field_size, self.data.machine_manure_dry_mass,
                    self.data.machine_manure_field_coverage, self.data.machine_water_extractable_inorganic_phosphorus,
                    False)
            self.data.machine_water_extractable_inorganic_phosphorus = \
                machine_inorganic_results["new_phosphorus_pool_amount"]
            self.data.machine_inorganic_phosphorus_runoff = machine_inorganic_results["runoff_phosphorus"]
            self.data.annual_runoff_machine_manure_inorganic_phosphorus += \
                machine_inorganic_results["runoff_phosphorus"]
            self._add_infiltrated_phosphorus_to_soil(machine_inorganic_results["infiltrated_phosphorus"], field_size)

        if self.data.grazing_manure_dry_mass > 0 and self.data.grazing_manure_field_coverage > 0:
            grazer_organic_results = \
                self._determine_phosphorus_leached_from_surface(rainfall, runoff, field_size,
                                                                self.data.grazing_manure_dry_mass,
                                                                self.data.grazing_manure_field_coverage,
                                                                self.data.grazing_water_extractable_organic_phosphorus,
                                                                True)
            self.data.grazing_water_extractable_organic_phosphorus = \
                grazer_organic_results["new_phosphorus_pool_amount"]
            self.data.grazing_organic_phosphorus_runoff = grazer_organic_results["runoff_phosphorus"]
            self.data.annual_runoff_grazing_manure_organic_phosphorus += grazer_organic_results["runoff_phosphorus"]
            self._add_infiltrated_phosphorus_to_soil(grazer_organic_results["infiltrated_phosphorus"], field_size)

            grazer_inorganic_results = \
                self._determine_phosphorus_leached_from_surface(
                    rainfall, runoff, field_size, self.data.grazing_manure_dry_mass,
                    self.data.grazing_manure_field_coverage, self.data.grazing_water_extractable_inorganic_phosphorus,
                    False)
            self.data.grazing_water_extractable_inorganic_phosphorus = \
                grazer_inorganic_results["new_phosphorus_pool_amount"]
            self.data.grazing_inorganic_phosphorus_runoff = grazer_inorganic_results["runoff_phosphorus"]
            self.data.annual_runoff_grazing_manure_inorganic_phosphorus += grazer_inorganic_results["runoff_phosphorus"]
            self._add_infiltrated_phosphorus_to_soil(grazer_inorganic_results["infiltrated_phosphorus"], field_size)

    def _add_infiltrated_phosphorus_to_soil(self, infiltrated_phosphorus_amount: float, field_size: float) -> None:
        """This method adds phosphorus that was dissolved in rainfall to the soil profile as outlined in SurPhos.

        Parameters
        ----------
        infiltrated_phosphorus_amount : float
            The amount of phosphorus to be added to the soil profile (kg)
        field_size : float
            The size of the field (ha)

        References
        ----------
        SurPhos Theoretical, page 8, paragraph below [13]

        Notes
        -----
        This method follows what is outlined in SurPhos (theoretical documentation, page 8, paragraph just below eqn.
        [13]), which is that 80% of infiltrated phosphorus stays in the top 20 mm of soil, and the rest infiltrates
        deeper.

        """
        self.data.soil_layers[0].add_to_labile_phosphorus(0.8 * infiltrated_phosphorus_amount, field_size)
        self.data.soil_layers[1].add_to_labile_phosphorus(0.2 * infiltrated_phosphorus_amount, field_size)

    def _adjust_manure_moisture_factor(self, rainfall: float, temperature_factor: float) -> None:
        """Adjusts the moisture factor of manure on the soil surface based on the current day's precipitation level.

        Parameters
        ----------
        rainfall : float
            The amount of rainfall on the current day (mm)
        temperature_factor : float
            The temperature factor on the current day (unitless)

        """
        if self.data.machine_manure_dry_mass > 0 and self.data.machine_manure_field_coverage > 0:
            change_in_machine_manure_moisture = \
                self._determine_moisture_change(rainfall, self.data.machine_manure_moisture_factor,
                                                self.data.machine_manure_dry_mass,
                                                self.data.machine_manure_applied_mass, temperature_factor)
            self.data.machine_manure_moisture_factor += change_in_machine_manure_moisture
            self.data.machine_manure_moisture_factor = min(0.9, max(self.data.machine_manure_moisture_factor, 0.0))

        if self.data.grazing_manure_dry_mass > 0 and self.data.grazing_manure_field_coverage > 0:
            change_in_grazing_manure_moisture = \
                self._determine_moisture_change(rainfall, self.data.grazing_manure_moisture_factor,
                                                self.data.grazing_manure_dry_mass,
                                                self.data.grazing_manure_applied_mass, temperature_factor)
            self.data.grazing_manure_moisture_factor += change_in_grazing_manure_moisture
            self.data.grazing_manure_moisture_factor = min(0.9, max(self.data.grazing_manure_moisture_factor, 0.0))

    def _determine_decomposed_surface_manure(self, temperature_factor: float) -> Dict[str, float]:
        """This method calculates how much manure in both the machine and grazer-applied pools decompose on a given day,
            and how much the field coverage changes as a result.

        Parameters
        ----------
        temperature_factor : float
            The temperature factor on the current day (unitless)

        Returns
        -------
        Dict (keys listed below)
            decomposed_machine_manure_mass_change: change in the mass of machine-applied manure on the field surface
                decomposed on this day (kg)
            decomposed_machine_manure_coverage_change: change in field coverage of machine-applied manure on the field
                surface (unitless)
            decomposed_grazing_manure_mass_change: change in the mass of grazer-applied manure on the field surface
                decomposed on this day (kg)
            decomposed_grazing_manure_coverage_change: change in field coverage of machine-applied manure on the field
                surface (unitless)

        """
        manure_dry_matter_decomposition_rate = \
            max(0.0, self._determine_dry_matter_decomposition_rate(temperature_factor))
        decomposed_machine_manure_mass_change, decomposed_machine_manure_coverage_change = 0, 0
        if self.data.machine_manure_dry_mass > 0 and self.data.machine_manure_field_coverage > 0:
            decomposed_machine_manure_mass_change = min(
                (self.data.machine_manure_dry_mass * manure_dry_matter_decomposition_rate),
                self.data.machine_manure_dry_mass)
            decomposed_machine_manure_coverage_change = min(
                (decomposed_machine_manure_mass_change / self.data.machine_manure_dry_mass) *
                self.data.machine_manure_field_coverage, self.data.machine_manure_field_coverage)

        decomposed_grazing_manure_mass_change, decomposed_grazing_manure_coverage_change = 0, 0
        if self.data.grazing_manure_dry_mass > 0 and self.data.grazing_manure_field_coverage > 0:
            decomposed_grazing_manure_mass_change = min(
                (self.data.grazing_manure_dry_mass * manure_dry_matter_decomposition_rate),
                self.data.machine_manure_dry_mass)
            decomposed_grazing_manure_coverage_change = min(
                (decomposed_grazing_manure_mass_change / self.data.grazing_manure_dry_mass) *
                self.data.grazing_manure_field_coverage, self.data.grazing_manure_field_coverage)

        return_dict = {"decomposed_machine_manure_mass_change": decomposed_machine_manure_mass_change,
                       "decomposed_machine_manure_coverage_change": decomposed_machine_manure_coverage_change,
                       "decomposed_grazing_manure_mass_change": decomposed_grazing_manure_mass_change,
                       "decomposed_grazing_manure_coverage_change": decomposed_grazing_manure_coverage_change}
        return return_dict

    def _determine_assimilated_surface_manure(self, temperature_factor: float, field_size: float) -> Dict:
        """Determines how much manure is assimilated into the soil profile and how much the manure coverage is reduced
            by on the current day.

        Parameters
        ----------
        temperature_factor : float
            The temperature factor on the current day (unitless)
        field_size : float
            The area of the field (ha)

        Returns
        -------
        Dict (keys listed below)
            assimilated_machine_manure: amount of machine-applied manure that is assimilated on a given day (kg)
            machine_manure_coverage: amount of decrease in the fraction of field covered by machine-applied manure on a
                given day (unitless)
            assimilated_grazing_manure: amount of grazer-applied manure that is assimilated on a given day (kg)
            grazing_manure_coverage: amount of decrease in the fraction of field covered by machine-applied manure on a
                given day (unitless)

        """
        assimilated_machine_manure, machine_manure_coverage = 0, 0
        if self.data.machine_manure_dry_mass > 0 and self.data.machine_manure_field_coverage > 0:
            machine_manure_cover_area = self.data.machine_manure_field_coverage * field_size
            assimilated_machine_manure = max(0.0, self._determine_dry_manure_matter_assimilation(
                self.data.machine_manure_moisture_factor, temperature_factor, machine_manure_cover_area, False))
            assimilated_machine_manure = min(self.data.machine_manure_dry_mass, assimilated_machine_manure)
            machine_manure_coverage = max(0.0, (assimilated_machine_manure / self.data.machine_manure_dry_mass) *
                                          self.data.machine_manure_field_coverage)
            machine_manure_coverage = min(machine_manure_coverage, self.data.machine_manure_field_coverage)

        assimilated_grazing_manure, grazing_manure_coverage = 0, 0
        if self.data.grazing_manure_dry_mass > 0 and self.data.grazing_manure_field_coverage > 0:
            grazing_manure_cover_area = self.data.grazing_manure_field_coverage * field_size
            assimilated_grazing_manure = max(0.0, self._determine_dry_manure_matter_assimilation(
                self.data.grazing_manure_moisture_factor, temperature_factor, grazing_manure_cover_area, True))
            assimilated_grazing_manure = min(self.data.grazing_manure_dry_mass, assimilated_grazing_manure)
            grazing_manure_coverage = max(0.0, (assimilated_grazing_manure / self.data.grazing_manure_dry_mass) *
                                          self.data.grazing_manure_field_coverage)
            grazing_manure_coverage = min(grazing_manure_coverage, self.data.grazing_manure_field_coverage)

        return_dict = {"assimilated_machine_manure": assimilated_machine_manure,
                       "machine_manure_coverage": machine_manure_coverage,
                       "assimilated_grazing_manure": assimilated_grazing_manure,
                       "grazing_manure_coverage": grazing_manure_coverage}
        return return_dict

    # --- Static Methods ---
    @staticmethod
    def _determine_phosphorus_leached_from_surface(rainfall: float, runoff: float, field_size: float,
                                                   manure_dry_mass: float, field_coverage: float,
                                                   water_extractable_phosphorus: float, is_organic: bool) \
            -> Dict[str, float]:
        """This method determines how much phosphorus is leached from the given pool, how that phosphorus is distributed
            between runoff and soil infiltration, and how much phosphorus remains in the given pool.

        Parameters
        ----------
        rainfall : float
            The amount of rainfall on the current day (mm)
        runoff : float
            The amount of runoff from rainfall on the current day (mm)
        field_size : float
            Area of the field (ha)
        manure_dry_mass : float
            Dry-weight equivalent of manure on the field (kg)
        field_coverage : float
            Percent of the field covered by manure, in range [0.0, 1.0] (unitless)
        water_extractable_phosphorus : float
            The mass of the water extractable phosphorus pool that is being leached from (kg)
        is_organic : bool
            Is the phosphorus being leached organic (True / False)

        Returns
        -------
        Dict (keys listed below)
            new_phosphorus_pool_amount: amount of phosphorus in the pool after leaching from it (kg)
            infiltrated_phosphorus: amount of phosphorus that infiltrates into the soil profile (kg)
            runoff_phosphorus: amount of phosphorus that leaves the field dissolved in runoff (kg)

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
        rain_manure_dry_matter_ratio = Manure._determine_rain_manure_dry_matter_ratio(rainfall, manure_dry_mass,
                                                                                      area_covered_by_manure)

        distribution_factor = Manure._determine_phosphorus_distribution_factor(rainfall, runoff)

        if is_organic:
            water_extractable_phosphorus_leached = Manure._determine_water_extractable_organic_phosphorus_leached(
                water_extractable_phosphorus, rain_manure_dry_matter_ratio, True)
        else:
            water_extractable_phosphorus_leached = Manure._determine_water_extractable_inorganic_phosphorus_leached(
                water_extractable_phosphorus, rain_manure_dry_matter_ratio, True)

        water_extractable_phosphorus_leached = min(water_extractable_phosphorus, water_extractable_phosphorus_leached)

        runoff_dissolved_phosphorus_concentration = Manure._determine_water_extractable_phosphorus_runoff_concentration(
            water_extractable_phosphorus_leached, rainfall, field_size, distribution_factor)

        runoff_in_liters = runoff * (field_size * HECTARES_TO_SQUARE_MILLIMETERS) * CUBIC_MILLIMETERS_TO_LITERS

        phosphorus_lost_to_runoff_in_kg = (runoff_dissolved_phosphorus_concentration * runoff_in_liters) * \
            MILLIGRAMS_TO_KILOGRAMS

        infiltrated_phosphorus = max(0, water_extractable_phosphorus_leached - phosphorus_lost_to_runoff_in_kg)

        new_phosphorus_pool_amount = water_extractable_phosphorus - water_extractable_phosphorus_leached
        return_dict = {"new_phosphorus_pool_amount": new_phosphorus_pool_amount,
                       "infiltrated_phosphorus": infiltrated_phosphorus,
                       "runoff_phosphorus": phosphorus_lost_to_runoff_in_kg}
        return return_dict

    @staticmethod
    def _determine_assimilated_phosphorus_amount(assimilation_ratio: float, phosphorus_amount: float) -> float:
        """Calculates the amount of phosphorus that is removed through assimilation on a given day.

        Parameters
        ----------
        assimilation_ratio : float
            Ratio of manure mass assimilated to amount present before assimilation (unitless)
        phosphorus_amount : float
            The amount of phosphorus in the pool being removed from (kg)

        Returns
        -------
        float
            The amount of phosphorus removed from the pool (kg)

        """
        return min(phosphorus_amount, max(0.0, assimilation_ratio * phosphorus_amount))

    @staticmethod
    def _determine_mineralized_surface_phosphorus(phosphorus_amount: float, rate: float, temperature_factor: float,
                                                  moisture_factor: float) -> float:
        """Calculates the amount of phosphorus that mineralizes into water-extractable inorganic phosphorus on the
            current day from the given pool.

        Parameters
        ----------
        phosphorus_amount : float
            The amount of phosphorus in the pool that is being mineralized (kg)
        rate : float
            The rate factor for the type of phosphorus being mineralized (unitless)
        temperature_factor : float
            The temperature factor on the current day (unitless)
        moisture_factor : float
            The moisture factor of the given manure pool on the current day (unitless)

        Returns
        -------
        float
            The amount of phosphorus that is mineralized from that pool that is passed (kg)

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

        References
        ----------
        SurPhos Theoretical Documentation [11]

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
            Is the water extractable inorganic phosphorus from cow manure, and not poultry or swine manure
                                                                                                        (true / false)

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
            The amount of runoff from rainfall on the current day (mm)

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

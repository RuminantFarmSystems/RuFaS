from typing import Optional, Dict
from math import log, exp

from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from SC_redesign.Crop_and_Soil.crop_and_soil_constants import HECTARES_TO_SQUARE_MILLIMETERS, \
    LITERS_TO_CUBIC_MILLIMETERS, KILOGRAMS_TO_MILLIGRAMS

"""
This module incorporates equations from the SurPhos model to simulate the leaching of Phosphorus from fertilizer applied
to the soil surface being absorbed into the soil and/or removed from the field by runoff.
"""


class Fertilizer:

    def __init__(self, soil_data: Optional[SoilData] = None):
        self.data = soil_data or SoilData()  # initialize with defaults, if not given

    def do_fertilizer_phosphorus_operations(self, rainfall: float, runoff: float, field_size: float) -> None:
        """The main routine that updates phosphorus in surface-applied fertilizer on a daily basis.
        Args:
            rainfall: amount of rainfall on this day (mm)
            runoff: amount of runoff on this day (mm)
            field_size: size of the field (ha)
        """
        if rainfall > 0:
            self.data.rain_events_after_fertilizer_application += 1

        first_rainfall_occurred = rainfall and self.data.rain_events_after_fertilizer_application == 1

        if self.data.rain_events_after_fertilizer_application == 0 or first_rainfall_occurred:
            self._update_before_and_at_first_rain(rainfall, runoff, field_size)
        else:
            self._update_after_first_rain(rainfall, runoff, field_size)

        self.data.days_since_application += 1

    def _update_before_and_at_first_rain(self, rainfall: float, runoff: float, field_size: float) -> None:
        """Decides which operations to perform on fertilizer phosphorus on all days before the first rainfall after the
            last application of fertilizer phosphorus, and on the day of the first rainfall.
        Args:
            rainfall: amount of rainfall on this day (mm)
            runoff: amount of runoff on this day (mm)
            field_size: size of the field (ha)
        """
        no_phosphorus_absorbed = \
            (self.data.rain_events_after_fertilizer_application == self.data.days_since_application == 0) \
            or self.data.available_phosphorus_pool == 0
        if no_phosphorus_absorbed:
            return

        phosphorus_absorbed_only = self.data.rain_events_after_fertilizer_application == 0 \
            and self.data.days_since_application > 0 and self.data.available_phosphorus_pool > 0
        if phosphorus_absorbed_only:
            self._absorb_phosphorus_from_available_pool()
            return

        first_rainfall_occurred = self.data.rain_events_after_fertilizer_application == 1 \
            and self.data.available_phosphorus_pool > 0
        if first_rainfall_occurred and runoff == 0:
            self._add_to_labile_phosphorus(self.data.available_phosphorus_pool, field_size)
            self.data.available_phosphorus_pool = 0
            return
        elif first_rainfall_occurred and runoff > 0:
            amounts_to_remove = self._determine_leached_phosphorus(rainfall, runoff, field_size,
                                                                   self.data.available_phosphorus_pool)
            runoff_phosphorus_to_remove = amounts_to_remove["runoff_phosphorus"]
            absorbed_phosphorus_to_remove = amounts_to_remove["absorbed_phosphorus"]
            self.data.available_phosphorus_pool -= (runoff_phosphorus_to_remove + absorbed_phosphorus_to_remove)
            self.data.annual_runoff_fertilizer_phosphorus += runoff_phosphorus_to_remove
            self._add_to_labile_phosphorus(absorbed_phosphorus_to_remove, field_size)
            return

    def _update_after_first_rain(self, rainfall: float, runoff: float, field_size: float) -> None:
        """Decides which operations to perform on fertilizer phosphorus on all days after the first rainfall event.
        Args:
            rainfall: amount of rainfall on this day (mm)
            runoff: amount of runoff on this day (mm)
            field_size: size of the field (ha)
        """
        if rainfall == 0:
            return
        elif runoff == 0:
            solubilized_phosphorus = self.data.recalcitrant_phosphorus_pool * self.data.solubilizing_factor
            self.data.recalcitrant_phosphorus_pool -= solubilized_phosphorus
            self._add_to_labile_phosphorus(solubilized_phosphorus, field_size)
            return
        else:
            amounts_to_remove = self._determine_leached_phosphorus(rainfall, runoff, field_size,
                                                                   self.data.recalcitrant_phosphorus_pool)
            runoff_phosphorus_to_remove = amounts_to_remove["runoff_phosphorus"]
            absorbed_phosphorus_to_remove = amounts_to_remove["absorbed_phosphorus"]
            self.data.recalcitrant_phosphorus_pool -= (runoff_phosphorus_to_remove + absorbed_phosphorus_to_remove)
            self.data.annual_runoff_fertilizer_phosphorus += runoff_phosphorus_to_remove
            self._add_to_labile_phosphorus(absorbed_phosphorus_to_remove, field_size)
            return

    def add_fertilizer_phosphorus(self, fertilizer_phosphorus_applied: float) -> None:
        """Resets counters and adds to phosphorous pools when new fertilizer phosphorus is applied to the fields.
        Args:
            fertilizer_phosphorus_applied: amount of phosphorus applied to soil surface via fertilizer (kg)
        Details:
            When fertilizer phosphorus is applied to the field this method resets both the days_since_application and
            rain_events_after_fertilizer_application to 0, and adds the new phosphorus to the available and recalcitrant
            pools. It also updates the starting available phosphorus value to the new available phosphorus pool value.
            If the amount of fertilizer to be added is zero, no pool or counters will be modified.
        """
        if fertilizer_phosphorus_applied == 0:
            return
        self.data.available_phosphorus_pool += 0.75 * fertilizer_phosphorus_applied
        self.data.full_available_phosphorus_pool = self.data.available_phosphorus_pool
        self.data.recalcitrant_phosphorus_pool += 0.25 * fertilizer_phosphorus_applied
        self.data.days_since_application = 0
        self.data.rain_events_after_fertilizer_application = 0

    def _absorb_phosphorus_from_available_pool(self) -> float:
        """This function calculates the amount phosphorus to be absorbed from the available pool to the labile pool.
        Details:
            This function gets the fraction of the available phosphorus pool that should remain after phosphorus is
            absorbed into the soil, then calls another method to add the determined amount of phosphorus to the labile
            pool of the top layer of soil
        Returns:
            Amount of phosphorous lost from available pool to soil absorption (kg)
        """
        sorption_percent = self._determine_fraction_phosphorus_remaining(self.data.cover_factor,
                                                                         self.data.days_since_application)

        phosphorus_removed = self.data.available_phosphorus_pool - \
            (sorption_percent * self.data.full_available_phosphorus_pool)
        if phosphorus_removed < 0:
            phosphorus_removed = self.data.available_phosphorus_pool

        return phosphorus_removed

    def _determine_leached_phosphorus(self, rainfall: float, runoff: float, field_size: float, phosphorus_pool: float) \
            -> Dict[float, float]:
        """This method determines the amount of phosphorus removed from the pool passed to it and partitions the amount
            of phosphorus lost in total between soil absorption and runoff loss.
        Args:
            rainfall: amount of rainfall on this day (mm)
            runoff: amount of runoff on this day (mm)
            field_size: size of the field (ha)
            phosphorus_pool: either the available or recalcitrant pool of fertilizer phosphorus (kg)
        Returns:
            Dictionary with amounts of phosphorus lost to runoff and soil absorption (both in kg)
        """
        phosphorus_in_mg = phosphorus_pool * KILOGRAMS_TO_MILLIGRAMS
        distribution_factor = self._determine_phosphorus_distribution_factor(rainfall, runoff)
        rainfall_in_liters = rainfall * (field_size * HECTARES_TO_SQUARE_MILLIMETERS) * \
            (1 / LITERS_TO_CUBIC_MILLIMETERS)
        solubilized_phosphorus = phosphorus_pool * self.data.solubilizing_factor

        dissolved_phosphorus_concentration = self._determine_dissolved_phosphorus_concentration(
            phosphorus_in_mg, self.data.solubilizing_factor, distribution_factor, rainfall_in_liters)

        runoff_in_liters = runoff * (field_size * HECTARES_TO_SQUARE_MILLIMETERS) * (1 / LITERS_TO_CUBIC_MILLIMETERS)
        runoff_phosphorus_kg = (dissolved_phosphorus_concentration * runoff_in_liters) * (1 / KILOGRAMS_TO_MILLIGRAMS)

        runoff_phosphorus_kg = min(solubilized_phosphorus, runoff_phosphorus_kg)
        return_dict = {"runoff_phosphorus": runoff_phosphorus_kg}

        absorbed_phosphorus = solubilized_phosphorus - runoff_phosphorus_kg
        return_dict["absorbed_phosphorus"] = absorbed_phosphorus

        return return_dict

    def _add_to_labile_phosphorus(self, phosphorus_to_add: float, field_size: float) -> None:
        """This method adds a specified mass of phosphorus to the labile phosphorus content of the top layer of the soil
            profile.
        Args:
            phosphorus_to_add: amount of phosphorus to add (kg)
            field_size: size of the field (ha)
        Details:
            Before adding the mass of phosphorus to the labile phosphorus content, it first converts the current amount
            of labile phosphorus in the top layer of soil from kg per ha to kg, then adds the new phosphorus, then
            converts the new mass to kg per ha.
        """
        labile_phosphorus_mass = self.data.soil_layers[0].labile_phosphorus_content * field_size
        labile_phosphorus_mass += phosphorus_to_add
        self.data.soil_layers[0].labile_phosphorus_content = labile_phosphorus_mass / field_size

    # --- Static methods ---
    @staticmethod
    def _determine_fraction_phosphorus_remaining(cover_factor: float, days_since_application: int) -> float:
        """Determines fraction of phosphorus remaining in the available phosphorous pool
        Args:
            cover_factor: factor for calculating fraction of phosphorus remaining, based on the cover type (unitless)
            days_since_application: number of days since the last fertilizer application was made
        Returns:
            The fraction of phosphorus that remains in the available phosphorus pool (unitless)
        References:
            pseudocode_soil [S.5.C.I.1], SurPhos [14] (Note: constants differ between the documents, prefer the ones
            from pseudocode_soil)
        Details:
            The minimum fraction that can be returned is 0
        """
        return max(0, -0.16 * log(days_since_application) + cover_factor)

    @staticmethod
    def _determine_phosphorus_distribution_factor(rainfall: float, runoff: float) -> float:
        """This method determines the phosphorus distribution factor for use in determining how leached fertilizer
            phosphorus is distributed between infiltration and runoff
        Args:
            rainfall: amount of rainfall on this day (mm)
            runoff: amount of runoff on this day (mm)
        Returns:
            The phosphorus distribution factor (unitless)
        References:
            pseudocode_soil [S.5.C.II.2], SurPhos [15]
        """
        return 0.034 * exp(3.4 * (runoff / rainfall))

    @staticmethod
    def _determine_dissolved_phosphorus_concentration(fertilizer_phosphorus: float, fraction_phosphorus_released: float,
                                                      distribution_factor: float, total_rainfall: float) -> float:
        """Determines the concentration of phosphorus in the runoff
        Args:
            fertilizer_phosphorus: amount of fertilizer phosphorus in the pool that is going to be leached from (mg)
            fraction_phosphorus_released: fraction of phosphorus solubilized during the current rain event (unitless)
            distribution_factor: value that determines distribution of phosphorus between runoff and infiltration
                (unitless)
            total_rainfall: rainfall on this day (L)
        Returns:
            dissolved phosphorus concentration in runoff (mg per L)
        References:
            pseudocode_soil [S.5.C.II.3], SurPhos [16]
        """
        return (fertilizer_phosphorus * fraction_phosphorus_released * distribution_factor) / total_rainfall

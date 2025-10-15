from math import exp, log
from typing import Dict, Optional

from RUFAS.general_constants import GeneralConstants
from RUFAS.biophysical.field.soil.soil_data import SoilData


class Fertilizer:
    """
    Incorporates equations from the SurPhos model to simulate the leaching of Phosphorus from fertilizer applied to the
    soil surface, tracking its absorption into the soil and/or removal from the field by runoff.

    Parameters
    ----------
    soil_data : SoilData, optional
        The SoilData object used by this module to track all activity within the soil profile, creates new one if
        one is not provided.
    field_size : float, optional
        Used to initialize a SoilData object for this module to work with, if a pre-configured SoilData object is
        not provided (ha).

    Attributes
    ----------
    data : SoilData
        Holds the SoilData object for tracking Phosphorus leaching and other related processes.

    """

    def __init__(self, soil_data: Optional[SoilData], field_size: Optional[float] = None):
        self.data = soil_data or SoilData(field_size=field_size)

    def do_fertilizer_phosphorus_operations(self, rainfall: float, runoff: float, field_size: float) -> None:
        """
        Update phosphorus in surface-applied fertilizer on a daily basis.

        Parameters
        ----------
        rainfall : float
            Amount of rainfall on this day (mm).
        runoff : float
            Amount of runoff on this day (mm).
        field_size : float
            Size of the field (ha).

        """
        if rainfall > 0:
            self.data.rain_events_after_fertilizer_application += 1

        first_rainfall_occurred = rainfall and self.data.rain_events_after_fertilizer_application == 1

        self.data.runoff_fertilizer_phosphorus = 0.0

        if self.data.rain_events_after_fertilizer_application == 0 or first_rainfall_occurred:
            self._update_before_and_at_first_rain(rainfall, runoff, field_size)
        else:
            self._update_after_first_rain(rainfall, runoff, field_size)

        self.data.days_since_application += 1

    def _update_before_and_at_first_rain(self, rainfall: float, runoff: float, field_size: float) -> None:
        """
        Decide which operations to perform on fertilizer phosphorus.

        Parameters
        ----------
        rainfall : float
            Amount of rainfall on this day (mm).
        runoff : float
            Amount of runoff on this day (mm).
        field_size : float
            Size of the field (ha).

        """
        no_phosphorus_absorbed = (
            self.data.rain_events_after_fertilizer_application == self.data.days_since_application == 0
        ) or self.data.available_phosphorus_pool == 0
        if no_phosphorus_absorbed:
            return

        phosphorus_absorbed_only = (
            self.data.rain_events_after_fertilizer_application == 0
            and self.data.days_since_application > 0
            and self.data.available_phosphorus_pool > 0
        )
        if phosphorus_absorbed_only:
            self._absorb_phosphorus_from_available_pool(field_size)
            return

        first_rainfall_occurred = (
            self.data.rain_events_after_fertilizer_application == 1 and self.data.available_phosphorus_pool > 0
        )
        if first_rainfall_occurred and runoff == 0:
            self._add_phosphorus_to_soil(self.data.available_phosphorus_pool, field_size)
            self.data.available_phosphorus_pool = 0
            return
        elif first_rainfall_occurred and runoff > 0:
            amounts_to_remove = self._determine_leached_phosphorus(
                rainfall, runoff, field_size, self.data.available_phosphorus_pool
            )
            runoff_phosphorus_to_remove = amounts_to_remove["runoff_phosphorus"]
            absorbed_phosphorus_to_remove = amounts_to_remove["absorbed_phosphorus"]
            self.data.available_phosphorus_pool -= runoff_phosphorus_to_remove + absorbed_phosphorus_to_remove
            self.data.runoff_fertilizer_phosphorus = runoff_phosphorus_to_remove
            self.data.annual_runoff_fertilizer_phosphorus += runoff_phosphorus_to_remove
            self._add_phosphorus_to_soil(absorbed_phosphorus_to_remove, field_size)
            return

    def _update_after_first_rain(self, rainfall: float, runoff: float, field_size: float) -> None:
        """
        Decide which operations to perform on fertilizer phosphorus after the first rainfall event.

        Parameters
        ----------
        rainfall : float
            Amount of rainfall on this day (mm).
        runoff : float
            Amount of runoff on this day (mm).
        field_size : float
            Size of the field (ha).

        """
        if rainfall == 0:
            return
        elif runoff == 0:
            solubilized_phosphorus = self.data.recalcitrant_phosphorus_pool * self.data.solubilizing_factor
            self.data.recalcitrant_phosphorus_pool -= solubilized_phosphorus
            self._add_phosphorus_to_soil(solubilized_phosphorus, field_size)
            return
        else:
            amounts_to_remove = self._determine_leached_phosphorus(
                rainfall, runoff, field_size, self.data.recalcitrant_phosphorus_pool
            )
            runoff_phosphorus_to_remove = amounts_to_remove["runoff_phosphorus"]
            absorbed_phosphorus_to_remove = amounts_to_remove["absorbed_phosphorus"]
            self.data.recalcitrant_phosphorus_pool -= runoff_phosphorus_to_remove + absorbed_phosphorus_to_remove
            self.data.runoff_fertilizer_phosphorus = runoff_phosphorus_to_remove
            self.data.annual_runoff_fertilizer_phosphorus += runoff_phosphorus_to_remove
            self._add_phosphorus_to_soil(absorbed_phosphorus_to_remove, field_size)
            return

    def add_fertilizer_phosphorus(self, fertilizer_phosphorus_applied: float) -> None:
        """
        Resets counters and adds to phosphorus pools when new fertilizer phosphorus is applied to the fields.

        Parameters
        ----------
        fertilizer_phosphorus_applied : float
            Amount of phosphorus applied to soil surface via fertilizer (kg).

        Notes
        -------
        When fertilizer phosphorus is applied to the field, this method resets both the days_since_application and
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

    def _absorb_phosphorus_from_available_pool(self, field_size) -> None:
        """
        Calculate the amount of phosphorus to be absorbed from the available pool to the labile pool.

        Parameters
        ----------
        field_size : float
            Size of the field (ha).

        Notes
        -------
        This function calculates the amount of phosphorus to be absorbed from the available phosphorus pool to the
        labile pool in the soil. It determines the fraction of the available phosphorus pool that should remain after
        phosphorus is absorbed into the soil and then calls another method to add the determined amount of phosphorus to
        the labile pool of the top layer of soil.

        """
        sorption_percent = self._determine_fraction_phosphorus_remaining(
            self.data.cover_factor, self.data.days_since_application
        )

        phosphorus_absorbed = self.data.available_phosphorus_pool - (
            sorption_percent * self.data.full_available_phosphorus_pool
        )
        if phosphorus_absorbed < 0:
            phosphorus_absorbed = self.data.available_phosphorus_pool

        self.data.available_phosphorus_pool -= phosphorus_absorbed
        self.data.soil_layers[0].add_to_labile_phosphorus(phosphorus_absorbed, field_size)

    def _determine_leached_phosphorus(
        self, rainfall: float, runoff: float, field_size: float, phosphorus_pool: float
    ) -> Dict[str, float]:
        """
        Determine the amount of phosphorus removed from the specified pool and partition the loss between soil
        absorption and runoff.

        Parameters
        ----------
        rainfall : float
            Amount of rainfall on this day (mm).
        runoff : float
            Amount of runoff on this day (mm).
        field_size : float
            Size of the field (ha).
        phosphorus_pool : float
            Either the available or recalcitrant pool of fertilizer phosphorus (kg).

        Returns
        -------
        dict
            Dictionary with amounts of phosphorus lost to runoff and soil absorption (both in kg).

        """
        phosphorus_in_mg = phosphorus_pool * GeneralConstants.KG_TO_MILLIGRAMS
        distribution_factor = self._determine_phosphorus_distribution_factor(rainfall, runoff)
        rainfall_in_liters = (
            rainfall
            * (field_size * GeneralConstants.HECTARES_TO_SQUARE_MILLIMETERS)
            * (1 / GeneralConstants.LITERS_TO_CUBIC_MILLIMETERS)
        )
        solubilized_phosphorus = phosphorus_pool * self.data.solubilizing_factor

        dissolved_phosphorus_concentration = self._determine_dissolved_phosphorus_concentration(
            phosphorus_in_mg,
            self.data.solubilizing_factor,
            distribution_factor,
            rainfall_in_liters,
        )

        runoff_in_liters = (
            runoff
            * (field_size * GeneralConstants.HECTARES_TO_SQUARE_MILLIMETERS)
            * (1 / GeneralConstants.LITERS_TO_CUBIC_MILLIMETERS)
        )
        runoff_phosphorus_kg = (dissolved_phosphorus_concentration * runoff_in_liters) * (
            1 / GeneralConstants.KG_TO_MILLIGRAMS
        )

        runoff_phosphorus_kg = min(solubilized_phosphorus, runoff_phosphorus_kg)
        return_dict = {"runoff_phosphorus": runoff_phosphorus_kg}

        absorbed_phosphorus = solubilized_phosphorus - runoff_phosphorus_kg
        return_dict["absorbed_phosphorus"] = absorbed_phosphorus

        return return_dict

    def _add_phosphorus_to_soil(self, added_phosphorus: float, field_size: float) -> None:
        """
        Partitions and adds phosphorus to the top two soil layers.

        Parameters
        ----------
        added_phosphorus : float
            Phosphorus to be added to the soil profile (kg).
        field_size : float
            Size of the field (ha).

        Notes
        -----
        80% of added phosphorus goes into the surface soil layer, and 20% of it goes into the soil layer immediately
        below the surface soil layer. This distribution of phosphorus into the top two layers of soil is not explicitly
        stated to occur for phosphorus from chemical fertilizer, but is specified to happen for phosphorus from manure
        in the top paragraph of page 9 in the SurPhos Theoretical documentation. Pete Vadas instructed the use of this
        distribution of phosphorus for chemical fertilizer.

        """
        self.data.soil_layers[0].add_to_labile_phosphorus(0.8 * added_phosphorus, field_size)
        self.data.soil_layers[1].add_to_labile_phosphorus(0.2 * added_phosphorus, field_size)

    # --- Static methods ---
    @staticmethod
    def _determine_fraction_phosphorus_remaining(cover_factor: float, days_since_application: int) -> float:
        """
        Determine the fraction of phosphorus remaining in the available phosphorus pool.

        Parameters
        ----------
        cover_factor : float
            Factor for calculating the fraction of phosphorus remaining, based on the cover type (unitless).
        days_since_application : int
            Number of days since the last fertilizer application was made.

        Returns
        -------
        float
            The fraction of phosphorus that remains in the available phosphorus pool (unitless).

        References
        ----------
        pseudocode_soil [S.5.C.I.1], SurPhos [14]
            (Note: constants differ between the documents, prefer the ones from pseudocode_soil)

        Notes
        -------
        The minimum fraction that can be returned is 0.

        """
        return max(0, -0.16 * log(days_since_application) + cover_factor)

    @staticmethod
    def _determine_phosphorus_distribution_factor(rainfall: float, runoff: float) -> float:
        """
        Determine the phosphorus distribution factor for use in determining how leached fertilizer phosphorus is
        distributed
        between infiltration and runoff.

        Parameters
        ----------
        rainfall : float
            Amount of rainfall on this day (mm).
        runoff : float
            Amount of runoff on this day (mm).

        Returns
        -------
        float
            The phosphorus distribution factor (unitless).

        References
        ----------
        pseudocode_soil [S.5.C.II.2], SurPhos [15]

        """
        return 0.034 * exp(3.4 * (runoff / rainfall))

    @staticmethod
    def _determine_dissolved_phosphorus_concentration(
        fertilizer_phosphorus: float,
        fraction_phosphorus_released: float,
        distribution_factor: float,
        total_rainfall: float,
    ) -> float:
        """
        Determine the concentration of phosphorus in the runoff.

        Parameters
        ----------
        fertilizer_phosphorus : float
            Amount of fertilizer phosphorus in the pool that is going to be leached from (mg).
        fraction_phosphorus_released : float
            Fraction of phosphorus solubilized during the current rain event (unitless).
        distribution_factor : float
            Value that determines the distribution of phosphorus between runoff and infiltration (unitless).
        total_rainfall : float
            Rainfall on this day (L).

        Returns
        -------
        float
            Dissolved phosphorus concentration in runoff (mg per L).

        References
        ----------
        pseudocode_soil [S.5.C.II.3], SurPhos [16]

        """
        return (fertilizer_phosphorus * fraction_phosphorus_released * distribution_factor) / total_rainfall

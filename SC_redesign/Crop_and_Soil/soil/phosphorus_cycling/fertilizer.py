from typing import Optional
from math import log

from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData

"""
This module incorporates equations from the SurPhos model to simulate the Phosphorus from fertilizer applied to the soil
surface being absorbed into the soil or removed from the field by runoff.
"""


class Fertilizer:

    def __init__(self, soil_data: Optional[SoilData] = None):
        self.data = soil_data or SoilData()  # initialize with defaults, if not given

    def do_fertilizer_phosphorus_operations(self, rainfall: float, runoff: float,
                                            fertilizer_phosphorus_applied: float) -> None:
        """The main routine that updates phosphorus in surface-applied fertilizer on a daily basis.

        Args:
            rainfall: amount of rainfall on this day (mm)
            runoff: amount of runoff on this day (mm)
            fertilizer_phosphorus_applied: amount of phosphorus applied to soil surface via fertilizer (kg)

        """
        if fertilizer_phosphorus_applied > 0:
            self._adjust_pools_and_counters(fertilizer_phosphorus_applied)

        if rainfall > 0:
            self.data.rain_events_counter += 1

        no_phosphorus_moved = self.data.rain_events_counter == self.data.days_since_application == 0
        if no_phosphorus_moved:
            self.data.days_since_application += 1
            return

        # if self.data.rain_events_counter == 0:
        # fraction_remaining_phosphorus_available

    def _adjust_pools_and_counters(self, fertilizer_phosphorus_applied: float) -> None:
        """Resets counters and adds to phosphorous pools when new phosphorus is applied to the fields.

        Args:
            fertilizer_phosphorus_applied: amount of phosphorus applied to soil surface via fertilizer (kg)

        Details:
            When fertilizer phosphorus is applied to the field this method resets both the days_since_application and
            rain_events_counter to 0, and adds the new phosphorus to the available and recalcitrant pools.

        """
        self.data.available_phosphorus_pool += 0.75 * fertilizer_phosphorus_applied
        self.data.recalcitrant_phosphorus_pool += 0.25 * fertilizer_phosphorus_applied
        self.data.days_since_application = 0
        self.data.rain_events_counter = 0

    # --- Static methods ---
    @staticmethod
    def _determine_fraction_phosphorus_remaining(cover_factor: float, days_since_application: int) -> float:
        """Determines fraction of phosphorus remaining in the available phosphorous pool

        Args:
            cover_factor: factor for calculating fraction of phosphorus remaining, based on the cover type (unitless)
            days_since_application: number of days since the last fertilizer application was made

        Returns:
            The fraction of phosphorus that remains in the available phosphorus pool (unitless)

        Reference:
            pseudocode_soil [S.5.C.I.1], SurPhos [14] (Note: constants differ between the documents, prefer the ones
        from pseudocode_soil)

        Details:
            The minimum fraction that can be returned is 0
        """
        return max(0, -0.16 * log(days_since_application) + cover_factor)

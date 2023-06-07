from typing import List

from SC_redesign.Crop_and_Soil.manager.schedule import Schedule
from SC_redesign.Crop_and_Soil.manager.events import FertilizerEvent

"""
This module contains `FertilizerSchedule`, a `Schedule` child class that defines when and how much fertilizer will be 
applied to a field.
"""


class FertilizerSchedule(Schedule):

    def __init__(self, name: str, years: List[int], days: List[int], nitrogen_masses: List[float],
                 phosphorus_masses: List[float], application_depths: List[float] = None,
                 surface_remainder_fractions: List[float] = None, pattern_skip: int = 0, pattern_repeat: int = 0):
        """
        Creates and validates a fertilizer application schedule.

        Parameters
        ----------
        name : str
            Name of this fertilizer application schedule.
        years : List[int]
            Year(s) in which fertilizer will be applied.
        days : List[int]
            Day(s) in which fertilizer will be applied.
        nitrogen_masses : List[float]
            Minimum mass(es) of nitrogen in applications (kg)
        phosphorus_masses : List[float]
            Minimum mass(es) of phosphorus in applications (kg)
        application_depths : List[float], default=None
            Bottom depth(s) of fertilizer injection applications (mm)
        surface_remainder_fractions : List[float], default=None
            Fraction(s) of fertilizer application that remain on the the soil surface (unitless)

        Notes
        -----
        Application depths and surface remainder fractions actually have defaults of [0.0] and [1.0] respectively, but
        there are not specified in the signature because parameters cannot have mutable defaults.

        """
        super().__init__(name, years, days, pattern_skip, pattern_repeat)

        self.nitrogen_masses = self._elongate_list(nitrogen_masses, len(years))
        self.phosphorus_masses = self._elongate_list(phosphorus_masses, len(years))

        if application_depths is None:
            application_depths = [0.0]
        self.application_depths = self._elongate_list(application_depths, len(years))

        if surface_remainder_fractions is None:
            surface_remainder_fractions = [1.0]
        self.surface_remainder_fractions = self._elongate_list(surface_remainder_fractions, len(years))

        self._validate_fertilizer_parameters()

        self._validate_pattern_parameters()


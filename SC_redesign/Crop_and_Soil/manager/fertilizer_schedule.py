from typing import List, Any

from SC_redesign.Crop_and_Soil.manager.schedule import Schedule
from SC_redesign.Crop_and_Soil.manager.events import FertilizerEvent

"""
This module contains `FertilizerSchedule`, a `Schedule` child class that defines when and how much fertilizer will be
applied to a field.
"""


class FertilizerSchedule(Schedule):

    def __init__(self, name: str, mix_names: List[str], years: List[int], days: List[int], nitrogen_masses: List[float],
                 phosphorus_masses: List[float], application_depths: List[float] = None,
                 surface_remainder_fractions: List[float] = None, pattern_skip: int = 0, pattern_repeat: int = 0):
        """
        Creates and validates a fertilizer application schedule.

        Parameters
        ----------
        name : str
            Name of this fertilizer application schedule.
        mix_names : List[str]
            Name(s) of the specific fertilizer mix that fertilizer application is composed of.
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
            Fraction(s) of fertilizer application that remain on the soil surface (unitless)

        Notes
        -----
        Application depths and surface remainder fractions actually have defaults of [0.0] and [1.0] respectively, but
        there are not specified in the signature because parameters cannot have mutable defaults.

        """
        super().__init__(name, years, days, pattern_skip, pattern_repeat)

        self.mix_names = self._elongate_list(mix_names, len(years))
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

    def _validate_fertilizer_parameters(self) -> None:
        """
        Checks that all fields defining a fertilizer application schedule are valid, raises errors if not.

        Raises
        ------

        """
        error_header = f"'{self.name}': "

        valid_years = self._validate_years(self.years)
        if not valid_years:
            raise ValueError(error_header + f"expected all years to be > 0 and in non-descending order, received "
                                            f"'{self.years}'.")

        valid_days = self._validate_days(self.days)
        if not valid_days:
            raise ValueError(error_header + f"expected all days to be in range [1, 366], received '{self.days}'.")

        valid_nitrogen_masses = self._determine_if_all_non_negative_values(self.nitrogen_masses)
        if not valid_nitrogen_masses:
            raise ValueError(error_header + f"expected all nitrogen masses to be in >= 0, received "
                                            f"'{self.nitrogen_masses}'.")

        valid_phosphorus_masses = self._determine_if_all_non_negative_values(self.phosphorus_masses)
        if not valid_phosphorus_masses:
            raise ValueError(error_header + f"expected all phosphorus masses to be >= 0, received "
                                            f"'{self.phosphorus_masses}'.")

        valid_depths = self._determine_if_all_non_negative_values(self.application_depths)
        if not valid_depths:
            raise ValueError(error_header + f"expected all application depths to be >= 0, received "
                                            f"'{self.application_depths}'.")

        valid_fractions = all(0.0 <= fraction <= 1.0 for fraction in self.surface_remainder_fractions)
        if not valid_fractions:
            raise ValueError(error_header + f"expected all surface remainder fractions to be in range [0.0, 1.0], "
                                            f"received '{self.surface_remainder_fractions}'.")

        equal_fertilizer_parameters = len(self.years) == len(self.days) == len(self.mix_names) == \
            len(self.nitrogen_masses) == len(self.phosphorus_masses) == len(self.application_depths) == \
            len(self.surface_remainder_fractions)
        if not equal_fertilizer_parameters:
            raise ValueError(error_header + f"expected equal numbers of fertilizer application parameters, received "
                                            f"'{self.years}' years, '{self.days}' days, '{self.mix_names}' mix names, "
                                            f"'{self.nitrogen_masses}' nitrogen masses, '{self.phosphorus_masses}' "
                                            f"phosphorus masses, '{self.application_depths}' application depths, and "
                                            f"'{self.surface_remainder_fractions}' surface remainder fractions.")

    def generate_fertilizer_events(self) -> List[FertilizerEvent]:
        """
        Creates a list of all fertilizer application events that will occur as dictated by this fertilizer schedule.

        Returns
        -------
        List[FertilizerEvent]
            List of all fertilizer events that occur over the course of this fertilizer schedule.

        """
        all_years = self._repeat_pattern(self.years, self.pattern_skip, self.pattern_repeat)
        all_days = self.days * (self.pattern_repeat + 1)
        all_mix_names = self.mix_names * (self.pattern_repeat + 1)
        all_nitrogen_masses = self.nitrogen_masses * (self.pattern_repeat + 1)
        all_phosphorus_masses = self.phosphorus_masses * (self.pattern_repeat + 1)
        all_depths = self.application_depths * (self.pattern_repeat + 1)
        all_surface_fractions = self.surface_remainder_fractions * (self.pattern_repeat + 1)
        all_events = list(zip(all_mix_names, all_years, all_days, all_nitrogen_masses, all_phosphorus_masses,
                              all_depths, all_surface_fractions))

        fertilizer_events = []
        for event in all_events:
            new_event = FertilizerEvent(event[0], event[1], event[2], event[3], event[4], event[5], event[6])
            fertilizer_events.append(new_event)
        return fertilizer_events

    @staticmethod
    def _determine_if_all_non_negative_values(values: List[Any]) -> bool:
        """
        Checks that all values in a list are >= 0.

        Parameters
        ----------
        values : List[Any]
            List of values to be checked.

        Returns
        -------
        bool
            True if all values are >= 0, False otherwise.

        """
        return all(value >= 0 for value in values)

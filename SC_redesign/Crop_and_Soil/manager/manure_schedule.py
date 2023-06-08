from typing import List, Any

from SC_redesign.Crop_and_Soil.manager.schedule import Schedule
from SC_redesign.Crop_and_Soil.manager.events import ManureEvent

"""
This module contains `ManureSchedule`, a `Schedule` child class that defines when and how much manure will be applied to
a field.
"""


class ManureSchedule(Schedule):

    def __init__(self, name: str, years: [List], days: [List], nitrogen_masses: List[float],
                 phosphorus_masses: List[float], field_coverages: List[float], application_depths: List[float] = None,
                 surface_remainder_fractions: List[float] = None, pattern_skip: int = 0, pattern_repeat: int = 0):
        """
        Creates and validates a manure application schedule.

        Parameters
        ----------
        name : str
            Name of this manure schedule.
        years : List[int]
            Year(s) in which manure will be applied.
        days : List[int]
            Julian day(s) on which manure will be applied.
        nitrogen_masses : List[float]
            Minimum mass(s) of nitrogen that should be contained in manure applications (kg)
        phosphorus_masses : List[float]
            Minimum mass(s) of phosphorus that should be contained in manure applications (kg)
        field_coverages : List[float]
            Fraction(s) of the field covered by manure applications (unitless)
        application_depths : List[float], default=None
            Bottom depth(s) of manure injection applications (mm)
        surface_remainder_fractions : List[float], default=None
            Fractions(s) of manure application that remains on the soil surface (unitless)
        pattern_skip : int, default=0
            Number of years to skip between manure application schedule repetitions.
        pattern_repeat : int, default=0
            Number of times the specified manure application schedule should be repeated.

        Notes
        -----
        Application depths and surface remainder fractions actually have defaults of [0.0] and [1.0] respectively, but
        these are not specified in the signature because parameters cannot have mutable defaults.

        """
        super().__init__(name, years, days, pattern_skip, pattern_repeat)

        self.nitrogen_masses = self._elongate_list(nitrogen_masses, len(years))
        self.phosphorus_masses = self._elongate_list(phosphorus_masses, len(years))
        self.field_coverages = self._elongate_list(field_coverages, len(years))

        if application_depths is None:
            application_depths = [0.0]
        self.application_depths = self._elongate_list(application_depths, len(years))

        if surface_remainder_fractions is None:
            surface_remainder_fractions = [1.0]
        self.surface_remainder_fractions = self._elongate_list(surface_remainder_fractions, len(years))

        self._validate_manure_parameters()

        self._validate_pattern_parameters()

    def _validate_manure_parameters(self) -> None:
        """
        Checks that all parameters defining manure application schedule are valid, otherwise raises error.

        Raises
        ------
        ValueError
            If not all manure application years are valid.
        ValueError
            If not all manure application days are valid.
        ValueError
            If not all manure nitrogen masses are valid.
        ValueError
            If not all manure phosphorus masses are valid.
        ValueError
            If not all field coverage fractions are valid.
        ValueError
            If not all manure application depths are valid.
        ValueError
            If not all manure surface retention fractions are valid.
        ValueError
            If not all manure application parameters have the same length.

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
            raise ValueError(error_header + f"expected all nitrogen masses to be >= 0, received "
                                            f"'{self.nitrogen_masses}'.")

        valid_phosphorus_masses = self._determine_if_all_non_negative_values(self.phosphorus_masses)
        if not valid_phosphorus_masses:
            raise ValueError(error_header + f"expected all phosphorus masses to be >= 0, received "
                                            f"'{self.phosphorus_masses}'.")

        valid_coverage_fractions = all(0.0 <= fraction <= 1.0 for fraction in self.field_coverages)
        if not valid_coverage_fractions:
            raise ValueError(error_header + f"expected all field coverage fractions to be in the range [0.0, 1.0], "
                                            f"received '{self.field_coverages}'.")

        valid_depths = all(depth >= 0.0 for depth in self.application_depths)
        if not valid_depths:
            raise ValueError(error_header + f"expected all manure application depths to be >= 0, received "
                                            f"'{self.application_depths}'.")

        valid_surface_fractions = all(0.0 <= fraction <= 1.0 for fraction in self.surface_remainder_fractions)
        if not valid_surface_fractions:
            raise ValueError(error_header + f"expected all surface remainder fractions to be in the range [0.0, 1.0], "
                                            f"received '{self.surface_remainder_fractions}'.")

        equal_manure_application_parameters = len(self.years) == len(self.days) == len(self.nitrogen_masses) \
            == len(self.nitrogen_masses) == len(self.phosphorus_masses) == len(self.application_depths) \
            == len(self.surface_remainder_fractions)
        if not equal_manure_application_parameters:
            raise ValueError(error_header + f"expected equal number of manure application parameters, received "
                                            f"'{self.years}' years, '{self.days}' days, '{self.nitrogen_masses}' "
                                            f"nitrogen masses, '{self.phosphorus_masses}' phosphorus masses, "
                                            f"'{self.field_coverages}' field coverage fractions, "
                                            f"'{self.application_depths}' application depths, and "
                                            f"'{self.surface_remainder_fractions}' surface remainder fractions.")

    def generate_manure_events(self) -> List[ManureEvent]:
        """
        Creates a list of all manure applications that will be applied as dictated by this manure schedule.

        Returns
        -------
        List[ManureEvent]
            List of ManureEvents representing all manure applications that will occur over the simulation run.

        """
        all_years = self._repeat_pattern(self.years, self.pattern_skip, self.pattern_repeat)
        all_days = self.days * (self.pattern_repeat + 1)
        all_nitrogen_masses = self.nitrogen_masses * (self.pattern_repeat + 1)
        all_phosphorus_masses = self.phosphorus_masses * (self.pattern_repeat + 1)
        all_field_coverages = self.field_coverages * (self.pattern_repeat + 1)
        all_application_depths = self.application_depths * (self.pattern_repeat + 1)
        all_surface_remainder_fractions = self.surface_remainder_fractions * (self.pattern_repeat + 1)
        all_manure_application_events = list(zip(all_years, all_days, all_nitrogen_masses, all_phosphorus_masses,
                                                 all_field_coverages, all_application_depths,
                                                 all_surface_remainder_fractions))

        manure_application_events = []
        for event in all_manure_application_events:
            new_event = ManureEvent(year=event[0], day=event[1], nitrogen_mass=event[2], phosphorus_mass=event[3],
                                    field_coverage=event[4], application_depth=event[5],
                                    surface_remainder_fraction=event[6])
            manure_application_events.append(new_event)
        return manure_application_events

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

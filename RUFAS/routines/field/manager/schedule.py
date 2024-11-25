from typing import List

from RUFAS.routines.field.crop.harvest_operations import FINAL_HARVEST_OPERATIONS
from RUFAS.util import Utility


class Schedule:
    """
    Base class for scheduling events in the Crop and Soil module, provides a generic structure for creating and
    managing schedules for various agricultural and environmental processes.

    Parameters
    ----------
    name : str
        The name of the schedule, serving as a unique identifier.
    years : List[int]
        The years in which scheduled events are to occur.
    days : List[int]
        The Julian days corresponding to each event within the specified years.
    pattern_skip : int, optional, default 0.0
        The number of years to skip between repetitions of the schedule.
    pattern_repeat : int, optional, default 0.0
        The number of times the schedule pattern is repeated.

    Attributes
    ----------
    name : str
        Name of the schedule, uniquely identifying it within the simulation.
    years : List[int]
        List of years during which the scheduled events will occur.
    days : List[int]
        Elongated list of days to ensure a day value for each specified year, aligning with the `years` attribute.
    pattern_skip : int
        Specifies the interval of years between each cycle of the schedule.
    pattern_repeat : int
        Indicates how many times the schedule cycle is to be repeated.

    """

    def __init__(self, name: str, years: List[int], days: List[int], pattern_skip: int = 0, pattern_repeat: int = 0):
        self.name = name
        self.years = years

        self.days = Utility.elongate_list(days, len(years))

        self.pattern_skip = pattern_skip
        self.pattern_repeat = pattern_repeat
        Utility.validate_pattern_parameters(self.name, self.pattern_skip, self.pattern_repeat)

    @staticmethod
    def _validate_days(years: List[int], days: List[int]) -> bool:
        """
        Checks that all values passed for days are in the correct range.

        Parameters
        ----------
        years : List[int]
            Calendar year(s) in which this event will occur.
        days : List[int]
            Julian day(s) in which this event will occur.

        Returns
        -------
        bool
            True if all days are valid.

        Notes
        -----
        A day is 'valid' if it is in the range [1, 366] in leap years, and in the range [1, 365] in non-leap years.

        """
        dates = list(zip(years, days))
        for date in dates:
            if not Utility.is_leap_year(date[0]) and not 0 < date[1] <= 365:
                return False
            if Utility.is_leap_year(date[0]) and not 0 < date[1] <= 366:
                return False
        return True

    @staticmethod
    def _validate_years(years: List[int]) -> bool:
        """
        Checks that all years passed are valid and ordered.

        Parameters
        ----------
        years : List[int]

        Returns
        -------
        bool
            True if years are valid and ordered, False if not.

        Notes
        -----
        A list of years is valid if every year is > 0, and the list of years does not descend at all.

        """
        return all(0 < years[index] <= years[index + 1] for index in range(0, len(years) - 1))

    def generate_events(
        self,
        years: list[int],
        days: list[int],
        additional_attributes: list[list],
        event_class,
        pattern_skip: int,
        pattern_repeat: int,
        heat_scheduled: bool
    ) -> list:
        """
        Generic method to generate application events.

        Parameters
        ----------
        years : List[int]
            List of years for the schedule.
        days : List[int]
            List of days for the schedule.
        additional_attributes : List[List]
            Additional attributes for the events (e.g., nitrogen_mass, phosphorus_mass, etc.).
        event_class : class
            The class to instantiate for each event.
        pattern_skip : int
            Number of years to skip.
        pattern_repeat : int
            Number of times the pattern should repeat.
        heat_scheduled : bool
            Flag indicating if heat unit scheduling is utilized for harvesting decisions.

        Returns
        -------
        list
            List of instantiated event objects.
        """
        all_years = Utility.repeat_pattern(years, pattern_skip, pattern_repeat)
        all_days = days * (pattern_repeat + 1)
        repeated_attributes = [attr * (pattern_repeat + 1) for attr in additional_attributes]
        all_events = list(zip(all_years, all_days, *repeated_attributes))
        if heat_scheduled:
            all_events[:] = [
                harvest for harvest in all_events if harvest[2] in FINAL_HARVEST_OPERATIONS
            ]
        result = [event_class(*event) for event in all_events]

        return result

    @staticmethod
    def validate_depths(depths: List[float]) -> bool:
        """
        Checks that depths passed are all valid.

        Parameters
        ----------
        depths : List[float]
            List of tillage depths to be validated.

        Returns
        -------
        bool
            True if all tillage depths are valid, False otherwise.

        Notes
        -----
        Tillage depths must be > 0.

        """
        return all(depth > 0.0 for depth in depths)

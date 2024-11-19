from copy import copy
from typing import Any, List

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

    def _validate_pattern_parameters(self) -> None:
        """
        Checks the pattern skip and repeat parameters, if they are not correct raises errors.

        Raises
        ------
        ValueError
            If the skip is < 0.
            If the repeat is < 0.

        """
        if self.pattern_skip < 0:
            raise ValueError(f"'{self.name}': expected pattern skip to be >= 0, received '{self.pattern_skip}'.")
        if self.pattern_repeat < 0:
            raise ValueError(f"'{self.name}': expected pattern repeat to be >= 0, received '{self.pattern_repeat}'.")

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

    @staticmethod
    def _repeat_pattern(pattern: List[int], skip: int = 0, repeat: int = 0) -> List[int]:
        """
        Takes a pattern of numbers and repeats the pattern of differences between the numbers for a specified number of
        repetitions, skipping over specified gaps between repetitions.

        Parameters
        ----------
        pattern : List[int]
            The pattern to be repeated.
        skip : int
            Number of steps to skip between repeats (0 if no steps should be skipped).
        repeat : int
            Number of times pattern should be repeated.

        Returns
        -------
        List[int]
            The full repeated pattern of numbers.

        Examples
        --------
        >>> repeat_pattern([1, 3, 5], 1, 2)
        [1, 3, 5, 7, 9, 11, 13, 15, 17]

        >>> repeat_pattern([1, 3, 5], 0, 1)
        [1, 3, 5, 6, 8, 10]

        >>> repeat_pattern([2, 3, 7], 3, 2)
        [2, 3, 7, 11, 12, 16, 20, 21, 24]

        """
        differences = [skip + 1]
        in_pattern_differences = range(1, len(pattern[1:]) + 1)
        for difference in in_pattern_differences:
            differences.append(pattern[difference] - pattern[difference - 1])

        full_pattern = copy(pattern)
        differences_index = 0
        number_of_new_values = range(repeat * len(pattern))
        for _new_value in number_of_new_values:
            full_pattern.append(full_pattern[-1] + differences[differences_index])
            differences_index += 1
            differences_index %= len(pattern)
        return full_pattern

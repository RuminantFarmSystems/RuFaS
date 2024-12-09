from copy import copy
from typing import List, Any, Optional

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

    def __init__(self, name: str, years: list[int], days: list[int], pattern_skip: int = 0, pattern_repeat: int = 0):
        self.name = name
        self.years = years

        self.days = Utility.elongate_list(days, len(years))

        self.pattern_skip = pattern_skip
        self.pattern_repeat = pattern_repeat
        self.validate_pattern_parameters(self.name, self.pattern_skip, self.pattern_repeat)

    @staticmethod
    def _validate_days(years: list[int], days: list[int]) -> bool:
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
    def _validate_years(years: list[int]) -> bool:
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
        additional_attributes: Optional[list[Any]],
        additional_attributes_events: list[list[Any]],
        event_class: Any,
        pattern_skip: int,
        pattern_repeat: int,
        heat_scheduled_harvest: bool,
    ) -> list[Any]:
        """
        Generic method to generate application events.

        Parameters
        ----------
        years : List[int]
            List of years for the schedule.
        days : List[int]
            List of days for the schedule.
        additional_attributes : List[List]
            Additional general attributes for the events (e.g., crop reference).
        additional_attributes_events : List[List]
            Additional attributes for each of the events (e.g., nitrogen_mass, phosphorus_mass, etc.).
        event_class : class
            The class to instantiate for each event.
        pattern_skip : int
            Number of years to skip.
        pattern_repeat : int
            Number of times the pattern should repeat.
        heat_scheduled_harvest : bool
            Flag indicating if heat unit scheduling is utilized for harvesting decisions.

        Returns
        -------
        list
            List of instantiated event objects.

        """
        all_years = self.repeat_pattern(years, pattern_skip, pattern_repeat)
        all_days = days * (pattern_repeat + 1)
        repeated_attributes = [attr * (pattern_repeat + 1) for attr in additional_attributes_events]
        all_events = list(zip(all_years, all_days, *repeated_attributes))
        if heat_scheduled_harvest:
            all_events[:] = [harvest for harvest in all_events if harvest[2] in FINAL_HARVEST_OPERATIONS]
        result = [event_class(*additional_attributes, *event) for event in all_events]

        return result

    @staticmethod
    def validate_depths(depths: list[float]) -> bool:
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

        """
        return all(depth > 0.0 for depth in depths)

    @staticmethod
    def validate_equal_lengths(header: str, **kwargs: Any) -> bool:
        """
        Validates that all provided iterables have the same length.

        Parameters
        ----------
        header: str
            Error header when needs to throw an error.
        kwargs : list of iterables
            The iterables to check for length equality.

        Returns
        -------
        bool
            True if all lengths are equal.

        Raises
        ------
        ValueError
            If the lengths of the provided iterables are not all equal.
        """
        lengths = {key: len(value) for key, value in kwargs.items()}
        if len(set(lengths.values())) != 1:
            raise ValueError(
                f"{header} Mismatch in length of parameters. "
                f"Provided parameters are: {', '.join(f'{key}={value}' for key, value in kwargs.items())}. "
                f"Lengths are: {lengths}."
            )
        return True

    @classmethod
    def _validate_parameters(
        cls,
        non_negative_parameters: list[Optional[tuple[str, list[Any]]]],
        fraction_parameters: list[Optional[tuple[str, list[Any]]]],
        years: list[int],
        days: list[int],
        name: str,
    ) -> None:
        """
        General validations for schedule parameter.

        Parameters
        ----------
        non_negative_parameters: list[tuple[str, list]]
            A list of tuples containing parameter names and associated non-negative values.
        fraction_parameters: list[tuple[str, list]]
            A list of tuples containing parameter names and associated values that should be fractions.
        years: list[int]
            List of event years.
        days: list[int]
            List of event days.
        name : str
            The name of the schedule, serving as a unique identifier.

        Raises
        ------
        ValueError
            If non-negative values are negative.
            If fraction is out of range [0.0, 1.0].
            If not all years > 0 and in non-descending order.
            If not all days to be in range [1, 366].

        """
        valid_years = Schedule._validate_years(years)
        if not valid_years:
            raise ValueError(
                f"'{name}': " + f"expected all years to be > 0 and in non-descending order," f" received " f"'{years}'."
            )

        valid_days = Schedule._validate_days(years, days)
        if not valid_days:
            raise ValueError(f"'{name}': " + f"expected all days to be in range [1, 366], received '{days}'.")

        for parameter_name, parameter in non_negative_parameters:
            if not Utility.determine_if_all_non_negative_values(parameter):
                raise ValueError(
                    f"'{name}': " + f"expected all {parameter_name} to be" f" in >= 0, received '{parameter}'."
                )
        for parameter_name, parameter in fraction_parameters:
            if not Utility.validate_fractions(parameter):
                raise ValueError(
                    f"'{name}': " + f"expected all {parameter_name} to be in"
                    f" range [0.0, 1.0], "
                    f"received '{parameter}'."
                )

    @staticmethod
    def repeat_pattern(pattern: List[int], skip: int = 0, repeat: int = 0) -> list[int]:
        """
        Extends a pattern of numbers by repeating it a specified number of times. The pattern's differences between
        consecutive numbers are calculated and used for repetition, with an optional gap (skip) added between each
        repetition.

        Parameters
        ----------
        pattern : List[int | float]
            The pattern to be repeated.
        skip : int | float
            Number of steps to skip between repeats (0 if no steps should be skipped).
        repeat : int
            Number of times pattern should be repeated.

        Returns
        -------
        List[int]
            The full repeated pattern of numbers.

        Examples
        --------
        >>> Schedule.repeat_pattern([1, 3, 5], 1, 2)
        [1, 3, 5, 7, 9, 11, 13, 15, 17]
        First pattern [1, 3, 5] -> repeat the pattern with the difference of 2.
        Second repeated pattern [7, 9, 11] -> With a gap of 1 from last element of the last pattern (5).
        Third repeated pattern [13, 15, 17] -> Second pattern repetition with the same logic.

        >>> Schedule.repeat_pattern([1, 3, 5], 0, 1)
        [1, 3, 5, 6, 8, 10]

        >>> Schedule.repeat_pattern([2, 3, 7], 3, 2)
        [2, 3, 7, 11, 12, 16, 20, 21, 24]

        >>> Schedule.repeat_pattern([1, 2, 3], 0, 1)
        [1, 2, 3, 4, 5, 6]

        >>> Schedule.repeat_pattern([1, 2, 3], 1, 1)
        [1, 2, 3, 5, 6, 7]

        """
        if not pattern or repeat <= 0:
            return pattern
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

    @staticmethod
    def validate_pattern_parameters(name: str, pattern_skip: int, pattern_repeat: int) -> None:
        """
        Checks the pattern skip and repeat parameters, if they are not correct raises errors.

        Raises
        ------
        ValueError
            If the skip is < 0.
            If the repeat is < 0.

        """
        if pattern_skip < 0:
            raise ValueError(f"'{name}': expected pattern skip to be >= 0, received '{pattern_skip}'.")
        if pattern_repeat < 0:
            raise ValueError(f"'{name}': expected pattern repeat to be >= 0, received '{pattern_repeat}'.")

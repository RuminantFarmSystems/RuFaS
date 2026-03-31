from copy import copy
from typing import Any, Optional

from RUFAS.util import Utility


class Schedule:
    """
    Base class for scheduling events in the Crop and Soil module, provides a generic structure for creating and
    managing schedules for various agricultural and environmental processes.

    Parameters
    ----------
    name : str
        The name of the schedule, serving as a unique identifier.
    years : list[int]
        The years in which scheduled events are to occur.
    days : list[int]
        The Julian days corresponding to each event within the specified years.
    pattern_skip : int, optional, default 0.0
        The number of years to skip between repetitions of the schedule.
    pattern_repeat : int, optional, default 0.0
        The number of times the schedule pattern is repeated.

    Attributes
    ----------
    name : str
        Name of the schedule, uniquely identifying it within the simulation.
    years : list[int]
        List of years during which the scheduled events will occur.
    days : list[int]
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

    @staticmethod
    def _validate_days(years: list[int], days: list[int]) -> bool:
        """
        Checks that all values passed for days are in the correct range.

        Parameters
        ----------
        years : list[int]
            Calendar year(s) in which this event will occur.
        days : list[int]
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
    ) -> list[Any]:
        """
        Generic method to generate application events.

        Parameters
        ----------
        years : list[int]
            List of years for the schedule.
        days : list[int]
            List of days for the schedule.
        additional_attributes : list[List]
            Additional general attributes for the events (e.g., crop reference).
        additional_attributes_events : list[List]
            Additional attributes for each of the events (e.g., nitrogen_mass, phosphorus_mass, etc.).
        event_class : Any
            The class to instantiate for each event.
        pattern_skip : int
            Number of years to skip.
        pattern_repeat : int
            Number of times the pattern should repeat.

        Returns
        -------
        list
            List of instantiated event objects.

        """
        all_events = self.prepare_events(years, days, additional_attributes_events, pattern_skip, pattern_repeat)

        result = [event_class(*additional_attributes, *event) for event in all_events]

        return result

    def prepare_events(
        self,
        years: list[int],
        days: list[int],
        additional_attributes_events: list[list[Any]],
        pattern_skip: int,
        pattern_repeat: int,
    ) -> list[Any]:
        """
        Prepares the attributes to pass into the event classes constructor.

        Parameters
        ----------
        years : list[int]
            List of years for the schedule.
        days : list[int]
            List of days for the schedule.
        additional_attributes_events : list[list]
            Additional attributes for each of the events (e.g., nitrogen_mass, phosphorus_mass, etc.).
        pattern_skip : int
            Number of years to skip.
        pattern_repeat : int
            Number of times the pattern should repeat.

        Returns
        -------
        list
            list of prepared event arguments for event initialization.

        """
        all_years = self.repeat_pattern(years, pattern_skip, pattern_repeat)
        all_days = days * (pattern_repeat + 1)
        repeated_attributes = [attr * (pattern_repeat + 1) for attr in additional_attributes_events]
        all_events = list(zip(*repeated_attributes, all_years, all_days))
        return all_events

    @staticmethod
    def validate_positive_values(values: list[float]) -> bool:
        """
        Checks that values passed are greater than 0.

        Parameters
        ----------
        values : list[float]
            list of values to be validated.

        Returns
        -------
        bool
            True if all values are greater than 0, False otherwise.

        """
        return all(value > 0.0 for value in values)

    @staticmethod
    def validate_equal_lengths(header: str, **kwargs: Any) -> bool:
        """
        Validates that all provided iterables have the same length.

        Parameters
        ----------
        header: str
            Error header when for when an error is raised.
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

        Examples
        --------
        >>> Schedule.validate_equal_lengths("example", {"arg1": [1, 2, 3], "arg2": [4, 5, 6]})
        True

        >>> Schedule.validate_equal_lengths("example", {"arg1": [1, 2, 3], "arg2": [4, 5, 6, 7]})
        ValueError("example Mismatch in length of parameters. Provided parameters are: arg1=[1, 2, 3], arg2=[4, 5, 6, 7]
        . Lengths are: {'arg1': 3, 'arg2': 4}.")

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
            list of event years.
        days: list[int]
            list of event days.
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
    def repeat_pattern(pattern: list[int | float], skip: int = 0, repeat: int = 0) -> list[int]:
        """
        Extends a pattern of numbers by repeating it a specified number of times. The pattern's differences between
        consecutive numbers are calculated and used for repetition, with an optional gap (skip) added between each
        repetition.

        Parameters
        ----------
        pattern : list[int | float]
            The pattern to be repeated.
        skip : int
            Number of steps to skip between repeats (0 if no steps should be skipped).
        repeat : int
            Number of times pattern should be repeated.

        Returns
        -------
        list[int]
            The full repeated pattern of numbers.

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

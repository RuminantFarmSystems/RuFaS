from typing import List
from copy import deepcopy


class Schedule:

    def __init__(self, name: str, years: List[int], days: List[int], pattern_skip: int = 0, pattern_repeat: int = 0):
        """
        Creates a base Schedule object which specific types of Scheduling classes will inherit from.

        Parameters
        ----------
        name : str
            Reference to the name of this schedule that will be used to distinguish this schedule from others.
        years : List[int]
            Year(s) in which this event will occur.
        days : List[int]
            Day(s) in which this event will occur.
        pattern_skip : int, default=0
            Number of years to skip between cycles.
        pattern_repeat : int, default=0
            Number of times the specified pattern of this schedule should be repeated.

        Notes
        -----
        It is expected that this generic schedule class will only see use through its child classes, and for the errors
        raised they are expected to be caught by child classes and given more appropriate and specific error messages.

        """
        self.name = name
        self.years = years

        self.days = days
        if len(self.days) == 1:
            self.days *= len(self.years)

        self.pattern_skip = pattern_skip
        self.pattern_repeat = pattern_repeat

    def _validate_pattern_parameters(self) -> None:
        """
        Checks the pattern skip and repeat parameters, if they are not correct raises errors.

        Raises
        ------
        ValueError
            If the skip is < 0.
        ValueError
            If the repeat is < 0.

        """
        if self.pattern_skip < 0:
            raise ValueError(f"'{self.name}': expected pattern skip to be >= 0, received '{self.pattern_skip}'.")
        if self.pattern_repeat < 0:
            raise ValueError(f"'{self.name}': expected pattern repeat to be >= 0, received '{self.pattern_repeat}'.")

    @staticmethod
    def _validate_days(days: List[int]) -> bool:
        """
        Checks that all values passed for days are in the correct range.

        Parameters
        ----------
        days : List[int]
            Day(s) in which this event will occur.

        Returns
        -------
        bool
            True if all days are valid.

        Notes
        -----
        A day is 'valid' if it in the range [1, 366].

        """
        return all(0 < day <= 366 for day in days)

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
        Takes a pattern of numbers and repeats it a specified number of times, skipping over specified gaps between
        repetitions.

        Parameters
        ----------
        pattern : List[int]
            The pattern to be repeated.
        skip : int
            Number of steps to skip between repeats.
        repeat : int
            Number of times patter should be repeated.

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

        full_pattern = deepcopy(pattern)
        differences_index = 0
        number_of_new_values = range(repeat * len(pattern))
        for _new_value in number_of_new_values:
            full_pattern.append(full_pattern[-1] + differences[differences_index])
            differences_index += 1
            differences_index %= len(pattern)
        return full_pattern

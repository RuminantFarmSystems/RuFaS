from typing import List
from copy import deepcopy


class Schedule:

    def __init__(self, name: str, years: List[int], days: List[int], pattern_skip: int = 0, pattern_repeat: int = 0):
        """
        Creates a base Schedule object which specific types of Scheduling classes will inherit from.

        Parameters
        ----------
        name : str
            Reference to the name of this crop schedule that will be used to distinguish this schedule from others.
        years : List[int]
            Year(s) in which this event will occur.
        days : List[int]
            Day(s) in which this event will occur.
        pattern_skip : int, default=0
            Number of years to skip between cycles.
        pattern_repeat : int, default=0
            Number of times the specified crop planting and harvesting pattern should be repeated.

        Raises
        ------
        ValueError
            If the number of years is not equal to the number of days.
        ValueError
            If the pattern skip is less than 0.
        ValueError
            If the number of pattern repetitions is less than 0.

        """
        self.name = name

        days_valid = self._validate_days(days)
        if not days_valid:
            raise ValueError(f"Expected all days to be in range [1, 366], received `{days}`.")
        self.days = days

        years_valid = self._validate_years(years)
        if not years_valid:
            raise ValueError(f"Expected all years to be > 0 and in non-descending order, received `{years}`")
        self.years = years

        if len(self.days) == 1:
            self.days *= len(self.years)

        if len(self.days) != len(self.years):
            raise ValueError("Number of years and days must be equal.")

        if pattern_skip < 0:
            raise ValueError(f"Expected pattern skip to be >= 0, received '{pattern_skip}'.")
        elif pattern_repeat < 0:
            raise ValueError(f"Expected pattern repeat to be >= 0, received '{pattern_repeat}'.")
        self.pattern_skip = pattern_skip
        self.pattern_repeat = pattern_repeat

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
        for day in days:
            if not 0 < day <= 366:
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
        if not years[0] > 0:
            return False

        for index in range(1, len(years) - 1):
            year_valid = years[index]
            not_descending = years[index - 1] <= years[index]
            if not year_valid or not not_descending:
                return False

        return True

    @staticmethod
    def repeat_pattern(pattern: List[int], skip: int = 0, repeat: int = 0) -> List[int]:
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

        Raises
        ------
        ValueError
            If the skip is less than 0.
        ValueError
            If the number of times to repeat is less than 0.

        Examples
        --------
        >>> repeat_pattern([1, 3, 5], 1, 2)
        [1, 3, 5, 7, 9, 11, 13, 15, 17]

        >>> repeat_pattern([1, 3, 5], 0, 1)
        [1, 3, 5, 6, 8, 10]

        >>> repeat_pattern([2, 3, 7], 3, 2)
        [2, 3, 7, 11, 12, 16, 20, 21, 24]

        """
        if skip < 0:
            raise ValueError(f"Expected skip to be >= 0, received '{skip}'.")
        if repeat < 0:
            raise ValueError(f"Expected repeat to be >= 0, received '{repeat}'.")

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

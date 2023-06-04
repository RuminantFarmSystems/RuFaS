from typing import List
from copy import deepcopy

from SC_redesign.Crop_and_Soil.crop.harvest_operations import FINAL_HARVEST_OPERATIONS
from SC_redesign.Crop_and_Soil.manager.events import PlantingEvent, HarvestEvent

"""
The `CropSchedule` module allows users to specify a pattern for planting and harvesting a certain crop that can be
repeated over a specified number of years, with specified breaks in between repetitions of the pattern.
"""


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


class CropSchedule(Schedule):

    def __init__(self, name: str, crop_reference: str, planting_years: List[int], planting_days: List[int],
                 harvest_years: List[int], harvest_days: List[int], harvest_operations: List[str],
                 use_heat_scheduling: bool = False, pattern_skip: int = 0, pattern_repeat: int = 0):
        """
        Creates a CropSchedule instance based on user input.

        Parameters
        ----------
        name : str
            Reference to the name of this crop schedule that will be used to distinguish this schedule from others.
        crop_reference : str
            Reference to name of the crop that will be used to identify the correct crop specifications.
        planting_years : int | List[int]
            Year(s) in which crop is planted.
        planting_days : int | List[int]
            Day(s) on which crop is planted.
        harvest_years : int | List[int]
            Year(s) in which crop is harvested.
        harvest_days : int | List[int]
            Day(s) on which crop is harvested.
        harvest_operations : str | List[str]
            Operation(s) with which a crop is harvested.
        use_heat_scheduling : bool, default=False
            Variable indicating if heat scheduling should be used to determine when crop is harvested.
        pattern_skip : int, default=0
            Number of years to skip between cycles.
        pattern_repeat : int, default=0
            Number of times the specified crop planting and harvesting pattern should be repeated.

        Raises
        ------
        ValueError
            If the number of planting years is not equal to the number of planting days.
        ValueError
            If the number of harvest years, days, and operations are not equal.
        ValueError
            If the last harvest operation is not a valid final harvest operation, or if any of the operations before the
            last are final operations.
        ValueError
            If the pattern skip is less than 0.
        ValueError
            If the number of pattern repetitions is less than 0.

        Notes
        -----
        If use_heat_scheduling is True, then all non-final harvest events will be ignored.

        """
        try:
            super().__init__(name, planting_years, planting_days, pattern_skip, pattern_repeat)
        except ValueError as e:
            error_message = str(e)
            if error_message == f"Expected all days to be in range [1, 366], received `{planting_days}`.":
                raise ValueError(f"Expected all planting days to be in range [1, 366], received `{planting_days}`.")
            elif error_message == f"Expected all years to be > 0 and in non-descending order, received " \
                                  f"`{planting_years}`":
                raise ValueError(f"Expected all years to be > 0 and in non-descending order, received "
                                 f"`{planting_years}`")
            elif error_message == "Number of years and days must be equal.":
                raise ValueError("Number of years and days must be equal.")

        self.crop_reference = crop_reference
        self.planting_years = self.years
        self.planting_days = self.days

        harvest_days_valid = self._validate_days(harvest_days)
        if not harvest_days_valid:
            raise ValueError(f"Expected all harvest days to be in range [1, 366], received `{harvest_days}`.")
        self.harvest_days = harvest_days

        harvest_years_valid = self._validate_years(harvest_years)
        if not harvest_years_valid:
            raise ValueError(f"Expected all harvest years to be > 0 and in non-descending order, received "
                             f"`{harvest_years}`")
        self.harvest_years = harvest_years

        if len(self.harvest_days) == 1:
            self.harvest_days *= len(self.harvest_years)

        if len(harvest_operations) == 1:
            harvest_operations *= len(self.harvest_years)
        self.harvest_operations = harvest_operations

        equal_harvest_parameters = len(self.harvest_years) == len(self.harvest_days) == len(self.harvest_operations)
        if not equal_harvest_parameters:
            raise ValueError("Number of values for harvest years, days, and operations must be equal.")

        last_kills = self.harvest_operations[-1] in FINAL_HARVEST_OPERATIONS
        others_dont_kill = all(self.harvest_operations[:-1]) not in FINAL_HARVEST_OPERATIONS
        only_last_kills = last_kills and others_dont_kill
        if not only_last_kills:
            raise ValueError(f"Expected the final harvest operation to be the only one that kills the crop, received "
                             f"'{self.harvest_operations}'.")

        self.heat_scheduled = use_heat_scheduling

    def generate_planting_events(self) -> List[PlantingEvent]:
        """
        Generates a list of all planting events that should happen for this crop schedule.

        Returns
        -------
        List[PlantingEvent]
            List of all planting events that will happen for this crop schedule.

        """
        all_planting_years = PlantingEvent.repeat_pattern(self.planting_years, self.pattern_skip, self.pattern_repeat)
        all_planting_days = self.planting_days * (self.pattern_repeat + 1)
        all_planting_dates = list(zip(all_planting_years, all_planting_days))

        planting_events = []
        for date in all_planting_dates:
            new_planting_event = PlantingEvent(self.crop_reference, date[0], date[1], self.heat_scheduled)
            planting_events.append(new_planting_event)
        return planting_events

    def generate_harvest_events(self) -> List[HarvestEvent]:
        """
        Generates a list of all harvest events that will occur in the crop schedule.

        Returns
        -------
        List[HarvestEvent]
            List of harvesting events that will happen for this crop schedule.

        Notes
        -----
        If heat scheduled harvesting is used, then only the final harvesting event (i.e. the one that kills it) will be
        scheduled, which is why this method contains the if block that removes all non-final harvest events.

        """
        all_harvesting_years = HarvestEvent.repeat_pattern(self.harvest_years, self.pattern_skip, self.pattern_repeat)
        all_harvesting_days = self.harvest_days * (self.pattern_repeat + 1)
        all_harvesting_operations = self.harvest_operations * (self.pattern_repeat + 1)
        all_harvesting_dates = list(zip(all_harvesting_years, all_harvesting_days, all_harvesting_operations))

        if self.heat_scheduled:
            all_harvesting_dates[:] = \
                [harvest for harvest in all_harvesting_dates if harvest[2] in FINAL_HARVEST_OPERATIONS]

        harvest_events = []
        for date in all_harvesting_dates:
            new_harvest_event = HarvestEvent(self.crop_reference, date[0], date[1], date[2])
            harvest_events.append(new_harvest_event)
        return harvest_events

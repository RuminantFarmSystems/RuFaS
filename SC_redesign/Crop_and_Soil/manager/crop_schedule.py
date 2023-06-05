from typing import List

from SC_redesign.Crop_and_Soil.manager.schedule import Schedule
from SC_redesign.Crop_and_Soil.crop.harvest_operations import FINAL_HARVEST_OPERATIONS
from SC_redesign.Crop_and_Soil.manager.events import PlantingEvent, HarvestEvent

"""
The `CropSchedule` module allows users to specify a pattern for planting and harvesting a certain crop that can be
repeated over a specified number of years, with specified breaks in between repetitions of the pattern.
"""


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
        planting_years : List[int]
            Year(s) in which crop is planted.
        planting_days : List[int]
            Day(s) on which crop is planted.
        harvest_years : List[int]
            Year(s) in which crop is harvested.
        harvest_days : List[int]
            Day(s) on which crop is harvested.
        harvest_operations : List[str]
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
            If the init() method of the base Schedule class raises a ValueError.
        ValueError
            If the number of harvest years, days, and operations are not equal.
        ValueError
            If the last harvest operation is not a valid final harvest operation, or if any of the operations before the
            last are final operations.
        ValueError
            If the pattern skip is less than 0.
        ValueError
            If the number of pattern repetitions is less than 0.

        """
        super().__init__(name, planting_years, planting_days, pattern_skip, pattern_repeat)

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

    def _validate_planting_parameters(self) -> None:
        """
        Checks fields that dictate planting for correctness, otherwise raises errors.

        Raises
        ------
        ValueError
            If not all planting years are valid.
        ValueError
            If not all planting days are valid.
        ValueError
            If not number of planting years and days are not equal.

        """
        valid_years = self._validate_years(self.planting_years)
        if not valid_years:
            raise ValueError(f"'{self.name}': expected all years to be > 0 and in non-descending order, received "
                             f"'{self.planting_years}'.")

        valid_days = self._validate_days(self.planting_days)
        if not valid_days:
            raise ValueError(f"'{self.name}': expected all planting days to be in range [1, 366], received "
                             f"'{self.planting_days}'.")

        if len(self.planting_years) != len(self.planting_days):
            raise ValueError(f"'{self.name}': expected number of planting years and days to be the same, received "
                             f"'{self.planting_years}' years and '{self.planting_days}' days.")

    def generate_planting_events(self) -> List[PlantingEvent]:
        """
        Generates a list of all planting events that should happen for this crop schedule.

        Returns
        -------
        List[PlantingEvent]
            List of all planting events that will happen for this crop schedule.

        """
        all_planting_years = self._repeat_pattern(self.planting_years, self.pattern_skip, self.pattern_repeat)
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
        all_harvesting_years = self._repeat_pattern(self.harvest_years, self.pattern_skip, self.pattern_repeat)
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

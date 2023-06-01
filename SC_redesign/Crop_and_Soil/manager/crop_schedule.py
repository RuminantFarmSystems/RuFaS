from typing import List, Any

from SC_redesign.Crop_and_Soil.crop.harvest_operations import FINAL_HARVEST_OPERATIONS
from SC_redesign.Crop_and_Soil.manager.events import PlantingEvent, HarvestEvent

"""
The `CropSchedule` module allows users to specify a pattern for planting and harvesting a certain crop that can be
repeated over a specified number of years, with specified breaks in between repetitions of the pattern.
"""


class CropSchedule:

    def __init__(self, crop_reference: str, planting_years: int | List[int], planting_days: int | List[int],
                 harvest_years: int | List[int], harvest_days: int | List[int], harvest_operations: str | List[str],
                 use_heat_scheduling: bool = False, pattern_skip: int = 0, pattern_repeat: int = 0):
        """
        Creates a CropSchedule instance based on user input.

        Parameters
        ----------
        crop_reference : str
            Reference to name of the crop that will be used to identify the correct configuration.
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
        self.crop_reference = crop_reference

        self.planting_years = self._convert_to_list(planting_years)
        self.planting_days = self._convert_to_list(planting_days)
        self.harvest_years = self._convert_to_list(harvest_years)
        self.harvest_days = self._convert_to_list(harvest_days)
        self.harvest_operations = self._convert_to_list(harvest_operations)

        if len(self.planting_days) == 1:
            self.planting_days *= len(self.planting_years)

        if len(self.planting_days) != len(self.planting_years):
            raise ValueError("Number of years that crops are planted in and days crops are planted on must be equal.")

        if len(self.harvest_days) == 1:
            self.harvest_days *= len(self.harvest_years)

        if len(self.harvest_operations) == 1:
            self.harvest_operations *= len(self.harvest_years)

        equal_harvest_parameters = len(self.harvest_years) == len(self.harvest_days) == len(self.harvest_operations)
        if not equal_harvest_parameters:
            raise ValueError("Number of values for harvest years, days, and operations must be equal.")

        last_kills = self.harvest_operations[-1] in FINAL_HARVEST_OPERATIONS
        others_dont_kill = all(self.harvest_operations[:-1]) not in FINAL_HARVEST_OPERATIONS
        only_last_kills = last_kills and others_dont_kill
        if not only_last_kills:
            raise ValueError(f"Expected the final harvest operation to be the only one that kills the crop, received "
                             f"'{self.harvest_operations}'.")

        if pattern_skip < 0:
            raise ValueError(f"Expected pattern skip to be >= 0, received '{pattern_skip}'.")
        elif pattern_repeat < 0:
            raise ValueError(f"Expected pattern repeat to be >= 0, received '{pattern_repeat}'.")
        self.pattern_skip = pattern_skip
        self.pattern_repeat = pattern_repeat

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

    @staticmethod
    def _convert_to_list(to_be_converted: Any) -> List:
        """
        Converts any arbitrary data into a list that contains that data.

        Parameters
        ----------
        to_be_converted : Any
            Data to be converted.

        Returns
        -------
        List
            The data passed contained in a list.

        Notes
        -----
        If the data passed is already a list, it doesn't do anything to it.

        """
        if type(to_be_converted) == list:
            return to_be_converted
        return [to_be_converted]

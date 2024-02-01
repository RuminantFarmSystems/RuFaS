from typing import List

from RUFAS.routines.field.manager.schedule import Schedule
from RUFAS.routines.field.crop.harvest_operations import HarvestOperation, FINAL_HARVEST_OPERATIONS
from RUFAS.routines.field.manager.events import PlantingEvent, HarvestEvent

"""
The `CropSchedule` module allows users to specify a pattern for planting and harvesting a certain crop that can be
repeated over a specified number of years, with specified breaks in between repetitions of the pattern.
"""


class CropSchedule(Schedule):

    def __init__(
            self,
            name: str,
            crop_reference: str,
            planting_years: List[int],
            planting_days: List[int],
            harvest_years: List[int],
            harvest_days: List[int],
            harvest_operations: List[str],
            use_heat_scheduling: bool = False,
            planting_skip: int = 0,
            harvesting_skip: int = 0,
            pattern_repeat: int = 0
    ):
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
            Julian day(s) on which crop is planted.
        harvest_years : List[int]
            Year(s) in which crop is harvested.
        harvest_days : List[int]
            Julian day(s) on which crop is harvested.
        harvest_operations : List[str]
            Operation(s) with which a crop is harvested.
        use_heat_scheduling : bool, default=False
            Variable indicating if heat scheduling should be used to determine when crop is harvested.
        planting_skip : int, default=0
            Number of years to skip between planting cycles.
        harvesting_skip : int, default=0
            Number of years to skip between harvesting cycles.
        pattern_repeat : int, default=0
            Number of times the specified crop planting and harvesting pattern should be repeated.

        """
        super().__init__(name, planting_years, planting_days, planting_skip, pattern_repeat)

        self.crop_reference = crop_reference
        self.planting_years = self.years
        self.planting_days = self.days
        self.planting_skip = planting_skip

        self._validate_planting_parameters()

        self.harvest_years = harvest_years
        self.harvest_days = self._elongate_list(harvest_days, len(harvest_years))
        self.harvesting_skip = harvesting_skip

        harvest_operations_enum_list = [HarvestOperation(operation) for operation in harvest_operations]

        self.harvest_operations = self._elongate_list(
            harvest_operations_enum_list,
            len(harvest_years)
        )

        self._validate_harvest_parameters()

        self.heat_scheduled = use_heat_scheduling

        self._validate_pattern_parameters()

        self.planting_skip = self.harvest_years[-1] - self.planting_years[-1]

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

        valid_days = self._validate_days(self.planting_years, self.planting_days)
        if not valid_days:
            raise ValueError(f"'{self.name}': expected all planting days to be in range [1, 366], received "
                             f"'{self.planting_days}'.")

        if len(self.planting_years) != len(self.planting_days):
            raise ValueError(f"'{self.name}': expected number of planting years and days to be the same, received "
                             f"'{self.planting_years}' years and '{self.planting_days}' days.")

    def _validate_harvest_parameters(self) -> None:
        """
        Checks fields that dictate harvesting of crop for correctness, otherwise raises errors.

        Raises
        ------
        ValueError
            If not all harvest years are valid.
        ValueError
            If not all harvest days are valid.
        ValueError
            If the number of harvest years, days, and operations are not equal.
        ValueError
            If the last harvest operation is not a final one, or if any operations before the last are final ones.

        """
        harvest_years_valid = self._validate_years(self.harvest_years)
        if not harvest_years_valid:
            raise ValueError(f"'{self.name}': expected all harvest years to be > 0 and in non-descending order, "
                             f"received '{self.harvest_years}'.")

        harvest_days_valid = self._validate_days(self.harvest_years, self.harvest_days)
        if not harvest_days_valid:
            raise ValueError(f"'{self.name}': expected all harvest days to be in range [1, 366], received "
                             f"'{self.harvest_days}'.")

        equal_harvest_parameters = len(self.harvest_years) == len(self.harvest_days) == len(self.harvest_operations)
        if not equal_harvest_parameters:
            raise ValueError(f"'{self.name}': expected number of values for harvest years, days, and operations to be "
                             f"equal, received '{self.harvest_years}' years, '{self.harvest_days}' days, and "
                             f"'{self.harvest_operations}' operations.")

        last_kills = self.harvest_operations[-1] in FINAL_HARVEST_OPERATIONS
        others_dont_kill = all(self.harvest_operations[:-1]) not in FINAL_HARVEST_OPERATIONS
        only_last_kills = last_kills and others_dont_kill
        if not only_last_kills:
            raise ValueError(f"'{self.name}': expected the final harvest operation to be the only one that kills the "
                             f"crop, received '{self.harvest_operations}'.")

    def generate_planting_events(self) -> List[PlantingEvent]:
        """
        Generates a list of all planting events that should happen for this crop schedule.

        Returns
        -------
        List[PlantingEvent]
            List of all planting events that will happen for this crop schedule.

        """
        all_planting_years = self._repeat_pattern(self.planting_years, self.planting_skip, self.pattern_repeat)
        all_planting_days = self.planting_days * (self.pattern_repeat + 1)
        all_planting_dates = list(zip(all_planting_years, all_planting_days))

        planting_events = []
        for date in all_planting_dates:
            new_planting_event = PlantingEvent(crop_reference=self.crop_reference, year=date[0], day=date[1],
                                               heat_scheduled_harvest=self.heat_scheduled)
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
        all_harvesting_years = self._repeat_pattern(self.harvest_years, self.harvesting_skip, self.pattern_repeat)
        all_harvesting_days = self.harvest_days * (self.pattern_repeat + 1)
        all_harvesting_operations = self.harvest_operations * (self.pattern_repeat + 1)
        all_harvesting_dates = list(zip(all_harvesting_years, all_harvesting_days, all_harvesting_operations))

        if self.heat_scheduled:
            all_harvesting_dates[:] = \
                [harvest for harvest in all_harvesting_dates if harvest[2] in FINAL_HARVEST_OPERATIONS]

        harvest_events = []
        for date in all_harvesting_dates:
            new_harvest_event = HarvestEvent(crop_reference=self.crop_reference, year=date[0], day=date[1],
                                             operation=date[2])
            harvest_events.append(new_harvest_event)
        return harvest_events

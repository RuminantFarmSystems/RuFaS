from RUFAS.biophysical.field.crop.harvest_operations import FINAL_HARVEST_OPERATIONS, HarvestOperation
from RUFAS.data_structures.events import HarvestEvent, PlantingEvent
from RUFAS.biophysical.field.manager.schedule import Schedule
from RUFAS.output_manager import OutputManager
from RUFAS.util import Utility


class CropSchedule(Schedule):
    """
    A class for defining a schedule for planting and harvesting crops, allows users to specify a pattern for planting
    and harvesting a certain crop that can be repeated over a specified number of years, with specified breaks in
    between repetitions of the pattern.

    Parameters
    ----------
    name : str
        Reference to the name of this crop schedule that will be used to distinguish this schedule from others.
    crop_reference : str
        Reference to the name of the crop that will be used to identify the correct crop specifications.
    planting_years : list[int]
        Years in which the crop is planted.
    planting_days : list[int]
        Julian days on which the crop is planted.
    harvest_years : list[int]
        Years in which the crop is harvested.
    harvest_days : list[int]
        Julian days on which the crop is harvested.
    harvest_operations : list[str]
        Operations with which the crop is harvested.
    use_heat_scheduling : bool, default False
        Indicates if heat scheduling should be used to determine when the crop is harvested.
    planting_skip : int, optional, default 0
        Number of years to skip between planting cycles.
    harvesting_skip : int, optional, default 0
        Number of years to skip between harvesting cycles.
    pattern_repeat : int, optional, default 0
        Number of times the specified crop planting and harvesting pattern should be repeated.

    Attributes
    ----------
    crop_reference : str
        Identifier for the crop associated with this schedule.
    planting_years : list[int]
        List of years in which planting events will occur.
    planting_days : list[int]
        Corresponding Julian days for planting.
    planting_skip : int
        Number of years to skip between planting events.
    harvest_years : list[int]
        List of years in which harvesting events will occur.
    harvest_days : list[int]
        Corresponding Julian days for harvesting.
    harvest_operations : list[HarvestOperation]
        Enumerated list of operations to perform at harvest.
    heat_scheduled : bool
        Flag indicating if heat unit scheduling is utilized for harvesting decisions.
    harvesting_skip : int, default 0.0
        Number of years to skip between harvesting cycles.

    Notes
    -----
    This class extends the ``Schedule`` class, adding specific functionality for managing agricultural crop schedules.
    It involves detailed tracking and management of planting and harvesting events, including optional heat scheduling
    for advanced crop management.

    """

    def __init__(
        self,
        name: str,
        crop_reference: str,
        planting_years: list[int],
        planting_days: list[int],
        harvest_years: list[int],
        harvest_days: list[int],
        harvest_operations: list[str],
        use_heat_scheduling: bool = False,
        planting_skip: int = 0,
        harvesting_skip: int = 0,
        pattern_repeat: int = 0,
    ):
        super().__init__(name, planting_years, planting_days, planting_skip, pattern_repeat)

        self.crop_reference = crop_reference
        self.planting_years = self.years
        self.planting_days = self.days
        self.planting_skip = planting_skip

        self._validate_planting_parameters()

        self.harvest_years = harvest_years
        self.harvest_days = Utility.elongate_list(harvest_days, len(harvest_years))
        self.harvesting_skip = harvesting_skip

        harvest_operations_enum_list = [HarvestOperation(operation) for operation in harvest_operations]

        self.harvest_operations = Utility.elongate_list(harvest_operations_enum_list, len(harvest_years))

        self._validate_harvest_parameters()

        self.heat_scheduled = use_heat_scheduling

    def _validate_planting_parameters(self) -> None:
        """
        Checks fields that dictate planting for correctness, otherwise raises errors.

        """
        self._validate_parameters([], [], self.planting_years, self.planting_days, self.name)

        self.validate_equal_lengths(self.name, planting_years=self.planting_years, planting_days=self.planting_days)

    def _validate_harvest_parameters(self) -> None:
        """
        Checks fields that dictate harvesting of crop for correctness, otherwise raises errors.

        Raises
        ------
        ValueError
            If the final harvest operation is not the only one that kills the crop.

        """
        self._validate_parameters([], [], self.harvest_years, self.harvest_days, self.name)

        self.validate_equal_lengths(
            self.name,
            planting_years=self.harvest_years,
            planting_days=self.harvest_days,
            harvest_operations=self.harvest_operations,
        )

        last_kills = self.harvest_operations[-1] in FINAL_HARVEST_OPERATIONS
        others_dont_kill = all(self.harvest_operations[:-1]) not in FINAL_HARVEST_OPERATIONS
        only_last_kills = last_kills and others_dont_kill
        if not only_last_kills:
            OutputManager().add_error(
                "Final harvest operation not a kill operation",
                f"'{self.name}': expected the final harvest operation to be the only one that kills the "
                f"crop, received '{self.harvest_operations}'.",
                info_map={"class": self.__class__.__name__, "function": self._validate_harvest_parameters.__name__},
            )
            raise ValueError(
                f"'{self.name}': expected the final harvest operation to be the only one that kills the "
                f"crop, received '{self.harvest_operations}'."
            )

    def generate_planting_events(self) -> list[PlantingEvent]:
        """
        Generates a list of all planting events that should happen for this crop schedule.

        Returns
        -------
        list[PlantingEvent]
            List of all planting events that will happen for this crop schedule.

        """
        return list(
            self.generate_events(
                self.planting_years,
                self.planting_days,
                [self.crop_reference, self.heat_scheduled],
                [],
                PlantingEvent,
                self.planting_skip,
                self.pattern_repeat,
            )
        )

    def generate_harvest_events(self) -> list[HarvestEvent]:
        """
        Generates a list of all harvest events that will occur in the crop schedule.

        Returns
        -------
        list[HarvestEvent]
            List of harvesting events that will happen for this crop schedule.

        Notes
        -----
        If heat scheduled harvesting is used, then only the final harvesting event (i.e. the one that kills it) will be
        scheduled, which is why this method contains the if block that removes all non-final harvest events.

        """
        all_events = self.prepare_events(
            self.harvest_years,
            self.harvest_days,
            [self.harvest_operations],
            self.harvesting_skip,
            self.pattern_repeat,
        )
        if self.heat_scheduled:
            all_events[:] = [harvest for harvest in all_events if harvest[0] in FINAL_HARVEST_OPERATIONS]
        result = [HarvestEvent(self.crop_reference, *event) for event in all_events]
        return result

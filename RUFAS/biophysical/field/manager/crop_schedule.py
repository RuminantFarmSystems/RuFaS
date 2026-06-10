from typing import Any

from RUFAS.biophysical.field.crop.harvest_operations import (
    FINAL_HARVEST_OPERATIONS,
    VALID_HARVEST_OPERATIONS,
    HarvestOperation,
)
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

    @staticmethod
    def validate_crop_schedule_event_order(rotation: dict[str, Any], schedule_name: str) -> None:
        """
        Validates that planting, harvest, and kill events occur in a biologically valid order.

        Parameters
        ----------
        rotation : dict[str, Any]
            Crop schedule definition from the crop rotation input file. Must contain the planting and harvest year/day
            information required to construct a chronological event sequence.
        schedule_name : str
            Name of the crop schedule being validated. Used for error reporting.

        Raises
        ------
        ValueError
            If a harvest or kill operation occurs before planting, or if one occurs after the crop has already been
            terminated and before another planting.

        Notes
        -----
        A crop must be planted before any harvest or kill operation can occur. Once an operation in
        ``FINAL_HARVEST_OPERATIONS`` occurs, including ``harvest_kill`` or ``kill_only``, no additional harvest or kill
        events are permitted until another planting event re-establishes the crop. These rules are evaluated
        chronologically across the entire schedule and are not reset at calendar year boundaries, allowing support for
        perennial and overwintering crops.

        """
        events: list[tuple[int, int, str | HarvestOperation]] = []

        for year, day in zip(rotation["planting_years"], rotation["planting_days"]):
            events.append((year, day, "planting"))

        for year, day, operation in zip(
            rotation["harvest_years"],
            rotation["harvest_days"],
            rotation["harvest_operations"],
        ):
            events.append((year, day, HarvestOperation(operation)))

        event_order = {
            "planting": 0,
            HarvestOperation.HARVEST_ONLY: 1,
            HarvestOperation.HARVEST_KILL: 1,
            HarvestOperation.KILL_ONLY: 1,
        }
        events.sort(key=lambda event: (event[0], event[1], event_order.get(event[2], 99)))

        has_live_crop = False

        for year, day, event_type in events:
            if event_type == "planting":
                has_live_crop = True
                continue

            if event_type in VALID_HARVEST_OPERATIONS:
                if not has_live_crop:
                    err_msg = (
                        f"Invalid crop schedule '{schedule_name}': {event_type.value} on "
                        f"year {year}, day {day} occurs before an active planting event. "
                        "A crop must be planted before any harvest or kill operation, and "
                        "after a terminating operation another planting must occur before "
                        "additional harvest or kill operations."
                    )
                    om = OutputManager()
                    info_map = {
                        "class": CropSchedule.__name__,
                        "function": CropSchedule.validate_crop_schedule_event_order.__name__,
                    }
                    om.add_error("Invalid crop schedule event order.", err_msg, info_map)
                    raise ValueError(err_msg)

                if event_type in FINAL_HARVEST_OPERATIONS:
                    has_live_crop = False

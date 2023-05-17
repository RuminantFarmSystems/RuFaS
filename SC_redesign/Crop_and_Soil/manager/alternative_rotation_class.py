from dataclasses import dataclass
from typing import List
from SC_redesign.Crop_and_Soil.crop.harvest_operations import HarvestOperation, FINAL_HARVEST_OPERATIONS
from SC_redesign.Crop_and_Soil.manager.Events import Event, HarvestEvent


class CropSchedule:
    """Specifies the timing of events for a single crop instance"""
    def __init__(self, crop_reference: str, planting_event: Event,
                 harvest_events: HarvestEvent | List[HarvestEvent] | None,
                 use_heat_scheduling: bool = False):
        """Creates a CropSchedule instance

        Parameters
        ----------
        crop_reference : str
            an identifier referencing the crop type to initialize. Either a supported `CropSpecies` or
            the name of a user-defined crop configuration.
        planting_event: Event
            an Event object that specifies when this the crop should be planted
        harvest_events: HarvestEvent | list[HarvestEvent], optional
            the HarvestEvent objects that indicate when harvest operations should be executed for this crop.
            multiple operations, specified with a list, are possible. In the case that multiple HarvestEvents
            are provided, the final HarvestEvent must terminate the crop, and the others must not. This argument
            is ignored and set to `None` if `use_heat_scheduling` is set to `True`.
        use_heat_scheduling : bool
            variable indicating whether heat scheduling should be used to determine when the crop is harvested. True
            ignores `harvest_events`.

        Raises
        ------
        Exception
            if `use_heat_scheduling` is False and the crop-terminating rules for `harvest_events` are not met.
        """
        self.crop_reference = crop_reference
        self.planting_event = planting_event
        self.use_heat_scheduling = use_heat_scheduling

        if use_heat_scheduling:
            self.harvest_events = None
            return

        if type(harvest_events) is HarvestEvent:
            self.harvest_events = [harvest_events]  # force to list
        else:
            self.harvest_events = harvest_events  # already a list

        last_kills = self.harvest_events[-1].operation in FINAL_HARVEST_OPERATIONS
        others_dont_kill = all(self.harvest_events[:-1]) not in FINAL_HARVEST_OPERATIONS
        only_last_kills = last_kills and others_dont_kill
        if not only_last_kills:
            raise Exception("The final element of harvest_events must specify an operation that will terminate "
                            "the crop and the non-final harvest_events must not terminate the crop.")

class CropSequence:
    """Specifies a sequence of planting and harvesting events for a single crop species.

    This class is a collection of CropSchedule instances with the same `crop_reference` attribute

    Attributes
    ----------
    crop_schedules : list[CropSchedule]
        a collection of CropSchedule for a single crop_reference.
    crop_reference : str
        the crop reference shared by all elements of crop_schedules
    """
    def __init__(self, crop_schedules: CropSchedule | List[CropSchedule]):
        """Creates an instance of CropSequence

        Raises
        ------
        Exception
            if all CropSchedule instances in crop_schedules do not share the same crop_reference attribute.
        """
        if type(crop_schedules) == CropSchedule:
            self.crop_schedules = [crop_schedules]  # coerce to list
        else:
            self.crop_schedules = crop_schedules  # already list

        same_crop = all([this.crop_reference == self.crop_schedules[0].crop_reference for this in self.crop_schedules])
        if not same_crop:
            raise Exception("all elements in crop_schedules should have the same crop_reference. For scheduling "
                            "sequences of multiple crops, see CropRotation.")
        self.crop_reference = self.crop_schedules[0].crop_reference

    @staticmethod
    def create_from_pattern():
        """creates a CropSequence object from a pattern. This more closely matches the structure that users will
        be inputting data to create the crop rotation schedule for a field or management unit."""
        pass


# @dataclass
# class CropRotation:
#     crop_ids: List[str]
#     """the identifier referencing the crop to initialize. Either a supported `CropSpecies` or the name of a
#     user-defined crop configuration."""
#     planting_specs: List[Event]
#     """the `Event` objects that determine when each crop gets initialized (planted)"""
#     harvest_specs: List[HarvestEvent | List[HarvestEvent]]
#     """the `HarvestEvent` objects that determine when (and how) each crop gets harvested"""
#
#     def __post_init__(self):
#         """"
#         Raises
#         ------
#         Exception
#             if the attributes are not equal length
#         """
#         if not len(self.crop_ids) == len(self.planting_specs) == len(self.harvest_specs):
#             raise Exception("crop_ids, planting_specs, and harvest_specs must all be the same length")
#
# if __name__ == '__main__':
#     # One crop, one harvest
#     one_simple = CropRotation(["corn"], [Event(0, 120)], [HarvestEvent(0, 240)])
#     # One crop, multiple harvests
#     one_complex = CropRotation(["alfalfa"],
#                                [Event(0, 120)],
#                                [[HarvestEvent(0, 180, "no_kill"),
#                                  HarvestEvent(0, 200, "no_kill"),
#                                  HarvestEvent(0, 240, "default")]])
#     # Two crops, different harvest patterns
#     corn_plant = Event(0, 120)
#     corn_harv = HarvestEvent(0, 240)
#     alf_plant = Event(1, 120)
#     alf_harv = [HarvestEvent(1, 240), HarvestEvent(2, 240), HarvestEvent(3, 240)]
#     two_complex = CropRotation(["corn", "alfalfa"], [corn_plant, alf_plant], [corn_harv, alf_harv])
#     # Corn, alf, alf, alf, corn, alf, alf, alf rotation
#
#     new_corn = corn_plant.project_next(1, 5)
#     print(new_corn.year, new_corn.day)
#     newer_corn = new_corn.project_next(2, 8)
#     print(newer_corn.year,newer_corn.day)

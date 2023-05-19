from typing import List
from SC_redesign.Crop_and_Soil.crop.harvest_operations import FINAL_HARVEST_OPERATIONS
from SC_redesign.Crop_and_Soil.manager.events import Event, HarvestEvent


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
    def create_from_sequences(crop_reference: str,
                              planting_years: List[int],
                              planting_days: List[int],
                              harvest_years: List[int | List[int]],
                              harvest_days: List[int | List[int]],
                              harvest_ops: List[str | List[str]]):
        # TODO: This method isn't working yet.
        """Creates a CropSequence object from sequences of event specifications

        Parameters
        ----------
        crop_reference : str
            the crop reference identifier for this sequence
        planting_years : list[int]
            the years, after simulation start, on which a new crop instances should be created
        planting_days : list[int]
            the day of the year on which new crops should be planted, one for each instance
        harvest_years : list[int | list[int]]
            the years on which the crop instances should be harvested, one element for each crop instance. If a single
            crop should be harvested over multiple years, the element can itself be a list with one value for each
            harvest event.
        harvest_days : list[int | list[int]]
            the days on which the crop instances should be harvested, one element for each crop instance. If a single
            crop should be harvested multiple times within a year, the element corresponding to that `harvest_years`
            element can itself be a list with one value per day for each year.
        harvest_ops : list[str | list[str]]
            the harvest operation that should occur at the time of harvest. This should have identical dimensions to
            harvest_days.

        Returns
        -------
        seq : CropSequence
            the resulting CropSequence object

        # TODO: See the below examples for how the code *should* work (as I see it, there's likely better way: tuples?)
        Examples
        --------
        Simple consecutive corn sequence:

        >>> CropSequence.create_from_sequences("corn", [0, 1, 2], [120, 120, 120], [0, 1, 2], [240, 240, 240]
        ...                                    ["default", "default", "default"])

        Alfalfa is planted once, and harvested multiple years:

        >>> CropSequence.create_from_sequences("alfalfa", [0], [120], [[0, 1, 2]], [[240, 240, 240]],
        ...                                    [["no_kill", "no_kill", "default"]])

        A crop may also need to be harvested twice per year, this is done by specifying the year multiple times:

        >>> CropSequence.create_from_sequences("imaginary crop", [0], [120], [[0, 0]], [[220, 240]],
        ...                                    [["no_kill", "default"]])

        This alfalfa is planted twice, it is harvested twice per year, for three years:

        >>> CropSequence.create_from_sequences(
        ...     crop_reference="grass", planting_years=[0, 3], planting_days=[120, 120],
        ...     harvest_years = [[0, 0, 1, 1, 2, 2], [3, 3, 4, 4, 5, 5]],
        ...     harvest_days = [[220, 240, 220, 240, 220, 240], [220, 240, 220, 240, 220, 240]],
        ...     harvest_ops = [["no_kill", "no_kill", "no_kill", "no_kill", "no_kill", "default"],
        ...                    ["no_kill", "no_kill", "no_kill", "no_kill", "no_kill", "default"]]
        ... )

        """
        if not len(planting_years) == len(planting_days) == len(harvest_days) == len(harvest_years) == len(harvest_ops):
            raise Exception("all input parameters must be lists of equal lengths")
        n_instances = len(planting_years)

        planting_events = []
        harvest_events = []
        for i in range(n_instances):
            py = planting_years[i]
            pd = planting_days[i]
            planting_events[i] = Event(py, pd)

            hy = harvest_years[i]
            if type(hy) is int:
                hy = [hy]
            hd = harvest_days[i]
            if type(hd) is int:
                hd = [hd]
            ho = harvest_ops[i]
            if type(ho) is str:
                ho = [ho]

            if not len(hd) == len(hy) == len(ho):
                raise Exception("sub-lists of harvest_years, harvest_days, and harvest_operations must have equal"
                                "lengths")
            n_years_harvested = len(hy)

            harvest_events[i] = []
            for j in range(n_years_harvested):
                y = hy[j]
                d = hd[j]
                if type(d) is int:
                    d = [d]
                o = ho[j]
                if type(o) is str:
                    o = [o]

                if len(d) != len(o):
                    raise Exception("harvest_days and harvest_operations must have equal dimensions")

                harvest_events[i][j] = [HarvestEvent(y, d, o)]

        schedules = [CropSchedule(crop_reference, p, h, False) for p, h in zip(planting_events, harvest_events)]
        return CropSequence(schedules)

    @staticmethod
    def create_from_pattern():
        """creates a CropSequence object from a pattern. This more closely matches the structure that users will
        be inputting data to create the crop rotation schedule for a field or management unit."""
        pass


class CropRotationSchedule:
    """Specifies the full crop-rotation schedule for a field over the course of the simulation.

    Attributes
    ----------
    crop_sequences : list[CropSequence]
        all the CropSequence objects, which specify when crops will be planted and harvest. Typically, there will be
        one element per species.
    """
    def __init__(self, crop_sequences: CropSequence | List[CropSequence]):
        if type(crop_sequences) is CropSequence:
            self.crop_sequences = [crop_sequences]
        else:
            self.crop_sequences = crop_sequences


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

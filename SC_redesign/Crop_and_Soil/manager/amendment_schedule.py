from typing import List

from SC_redesign.Crop_and_Soil.manager.crop_schedule import CropSchedule


class AmendmentSchedule:

    def __init__(self, years: int | List[int], days: int | List[int], pattern_skip: int = 0, pattern_repeat: int = 0):
        """
        Initializes a base soil amendment schedule.

        Parameters
        ----------
        years : int | List[int]
            Year(s) in which amendment will happen.
        days : int | List[int]
            Day(s) on which amendment will happen.
        pattern_skip : int, default=0
            Number of years to skip between amendment schedule repetitions.
        pattern_repeat : int, default=0
            Number of times the specified amendment schedule should be repeated.

        """
        self.years = CropSchedule.convert_to_list(years)
        self.days = CropSchedule.convert_to_list(days)

        if len(self.days) == 1:
            self.days *= days

        if len(self.days) != len(self.years):
            raise ValueError("Number of days that event occurs on must be 1 or equal to the number of years the event"
                             "occurs on.")

        if pattern_skip < 0:
            raise ValueError(f"Expected pattern skip to be >= 0, received '{pattern_skip}'.")
        self.pattern_skip = pattern_skip

        if pattern_repeat < 0:
            raise ValueError(f"Expected pattern repeat to be >= 0, received '{pattern_repeat}'.")
        self.pattern_repeat = pattern_repeat


class TillageSchedule(AmendmentSchedule):

    def __init__(self, years: int | List[int], days: int | List[int], pattern_skip: int = 0, pattern_repeat: int = 0):

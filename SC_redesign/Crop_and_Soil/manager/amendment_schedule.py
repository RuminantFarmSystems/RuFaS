from typing import List

from SC_redesign.Crop_and_Soil.manager.crop_schedule import CropSchedule
from SC_redesign.Crop_and_Soil.manager.events import TillageEvent


class AmendmentSchedule:

    def __init__(self, name: str, years: int | List[int], days: int | List[int], pattern_skip: int = 0,
                 pattern_repeat: int = 0):
        """
        Initializes a base soil amendment schedule.

        Parameters
        ----------
        name : str
            Name of this amendment schedule.
        years : int | List[int]
            Year(s) in which amendment will happen.
        days : int | List[int]
            Day(s) on which amendment will happen.
        pattern_skip : int, default=0
            Number of years to skip between amendment schedule repetitions.
        pattern_repeat : int, default=0
            Number of times the specified amendment schedule should be repeated.

        """
        self.name = name
        self.years = CropSchedule.convert_to_list(years)
        self.days = CropSchedule.convert_to_list(days)

        if len(self.days) == 1:
            self.days *= len(self.years)

        if len(self.days) != len(self.years):
            raise ValueError("Number of days that event occurs on must be 1 or equal to the number of years the event "
                             "occurs on.")

        if pattern_skip < 0:
            raise ValueError(f"Expected pattern skip to be >= 0, received '{pattern_skip}'.")
        self.pattern_skip = pattern_skip

        if pattern_repeat < 0:
            raise ValueError(f"Expected pattern repeat to be >= 0, received '{pattern_repeat}'.")
        self.pattern_repeat = pattern_repeat


class TillageSchedule(AmendmentSchedule):

    def __init__(self, name: str, years: int | List[int], days: int | List[int], tillage_depths: float | List[float],
                 incorporation_fractions: float | List[float], mixing_fractions: float | List[float],
                 pattern_skip: int = 0, pattern_repeat: int = 0):
        """
        Initializes a schedule for tilling.

        Parameters
        ----------
        name : str
            Name of this amendment schedule.
        years : int | List[int]
            Year(s) in which amendment will happen.
        days : int | List[int]
            Day(s) on which amendment will happen.
        tillage_depths : float | List[float]
            The lowest depth(s) the tilling implement reaches (mm)
        incorporation_fractions : List[float]
            Fraction(s) of soil surface pool incorporated into the soil profile (unitless)
        mixing_fractions : List[float]
            Fraction(s) of pool in each layer mixed and redistributed back into the soil profile (unitless)
        pattern_skip : int, default=0
            Number of years to skip between amendment schedule repetitions.
        pattern_repeat : int, default=0
            Number of times the specified amendment schedule should be repeated.

        """
        super().__init__(name=name, years=years, days=days, pattern_skip=pattern_skip, pattern_repeat=pattern_repeat)

        self.tillage_depths = CropSchedule.convert_to_list(tillage_depths)
        self.incorporation_fractions = CropSchedule.convert_to_list(incorporation_fractions)
        self.mixing_fractions = CropSchedule.convert_to_list(mixing_fractions)

        if len(self.tillage_depths) == 1:
            self.tillage_depths *= len(self.years)

        valid_depths = self._validate_depths(self.tillage_depths)
        if not valid_depths:
            raise ValueError(f"Expected all tillage depths to be > 0.0, received '{self.tillage_depths}'.")

        if len(self.incorporation_fractions) == 1:
            self.incorporation_fractions *= len(self.years)

        valid_fractions = self._validate_fractions(self.incorporation_fractions)
        if not valid_fractions:
            raise ValueError(f"Expected all incorporation fractions to be in range [0.0, 1.0], received "
                             f"'{self.incorporation_fractions}'.")

        if len(self.mixing_fractions) == 1:
            self.mixing_fractions *= len(self.years)

        valid_fractions = self._validate_fractions(self.mixing_fractions)
        if not valid_fractions:
            raise ValueError(f"Expected all mixing fractions to be in range [0.0, 1.0], received "
                             f"'{self.mixing_fractions}'.")

        equal_tillage_parameters = len(self.years) == len(self.tillage_depths) == len(self.incorporation_fractions) \
            == len(self.mixing_fractions)
        if not equal_tillage_parameters:
            raise ValueError("Number of years, days, depths, incorporation and mixing fractions must be equal.")

    def generate_tillage_events(self) -> TillageEvent:
        """
        Generates a list of all tillage events that will happen over the full course of this TillageSchedule.

        Returns
        -------
        List[TillageEvent]
            List of all tillage events that will happen over the course of this TillageSchedule.

        """
        all_tilling_years = TillageEvent.repeat_pattern(self.years, self.pattern_skip, self.pattern_repeat)
        all_tilling_days = self.days * (self.pattern_repeat + 1)
        all_tillage_depths = self.tillage_depths * (self.pattern_repeat + 1)
        all_incorporation_fractions = self.incorporation_fractions * (self.pattern_repeat + 1)
        all_mixing_fractions = self.mixing_fractions * (self.pattern_repeat + 1)
        all_tillage_events = list(zip(all_tillage_depths, all_incorporation_fractions, all_mixing_fractions,
                                      all_tilling_years, all_tilling_days))

        tillage_events = []
        for event in all_tillage_events:
            new_tillage_event = TillageEvent(event[0], event[1], event[2], event[3], event[4], event[5])
            tillage_events.append(new_tillage_event)
        return tillage_events

    @staticmethod
    def _validate_depths(tillage_depths: List[float]) -> bool:
        """
        Checks that tillage depths passed are all valid.

        Parameters
        ----------
        tillage_depths : List[float]
            List of tillage depths to be validated.

        Returns
        -------
        bool
            True if all tillage depths are valid, False otherwise.

        Notes
        -----
        Tillage depths must be > 0.

        """
        for depth in tillage_depths:
            if depth <= 0.0:
                return False
        return True

    @staticmethod
    def _validate_fractions(fractions: List[float]) -> bool:
        """
        Checks that all fractions passed are valid.

        Parameters
        ----------
        fractions : List[float]
            List of fractions to be valid

        Returns
        -------
        bool
            True if all fractions passed are valid, False otherwise.

        Notes
        -----
        A fraction is valid if it is in the range[0.0, 1.0]

        """
        for fraction in fractions:
            is_valid = 0.0 <= fraction <= 1.0
            if not is_valid:
                return False
        return True

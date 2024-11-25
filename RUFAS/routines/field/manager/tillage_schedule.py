from typing import List

from RUFAS.routines.EEE.enums import TillageImplement
from RUFAS.data_structures.events import TillageEvent
from RUFAS.routines.field.manager.schedule import Schedule


class TillageSchedule(Schedule):
    """
    A `Schedule` child class that defines when and how a field will be tilled.

    Parameters
    ----------
    name : str
        Name of this tillage schedule.
    years : List[int]
        Year(s) in which tillage will happen.
    days : List[int]
        Julian day(s) on which tillage will happen.
    tillage_depths : List[float]
        The lowest depth(s) the tilling implement reaches (mm).
    incorporation_fractions : List[float]
        Fraction(s) of soil surface pool incorporated into the soil profile (unitless).
    mixing_fractions : List[float]
        Fraction(s) of pool in each layer mixed and redistributed back into the soil profile (unitless).
    implements : List[str]
        Implements that are used to execute the tillage applications in this schedule.
    pattern_skip : int, default=0
        Number of years to skip between tillage schedule repetitions.
    pattern_repeat : int, default=0
        Number of times the specified tillage schedule should be repeated.

    Attributes
    ----------
    tillage_depths : List[float]
        Elongated list of tillage depths to ensure a depth value for each application year, representing how deep the
        tilling implement will go.
    incorporation_fractions : List[float]
        Elongated list of incorporation fractions to ensure an incorporation value for each application year, indicating
        how much of the surface soil is mixed into the profile.
    mixing_fractions : List[float]
        Elongated list of mixing fractions to ensure a mixing value for each application year, reflecting the degree of
        soil mixing during tillage.
    implements : List[TillageImplement]
        Elongated list of the tillage implements that will be used to execute the scheduled tillage operations.

    """

    def __init__(
        self,
        name: str,
        years: List[int],
        days: List[int],
        tillage_depths: List[float],
        incorporation_fractions: List[float],
        mixing_fractions: List[float],
        implements: List[str],
        pattern_skip: int = 0,
        pattern_repeat: int = 0,
    ):
        super().__init__(name, years, days, pattern_skip, pattern_repeat)

        self.tillage_depths = self._elongate_list(tillage_depths, len(years))
        self.incorporation_fractions = self._elongate_list(incorporation_fractions, len(years))
        self.mixing_fractions = self._elongate_list(mixing_fractions, len(years))

        self.implements = [TillageImplement(implement) for implement in implements]
        self.implements = self._elongate_list(self.implements, len(years))

        self._validate_tillage_parameters()

        self._validate_pattern_parameters()

    def _validate_tillage_parameters(self) -> None:
        """
        Checks all fields that define the tillage schedule and raises errors if any are invalid.

        Raises
        ------
        ValueError
            If not all tilling years are valid.
            If not all tilling days are valid.
            If not all tillage depths are valid.
            If not all incorporation fractions are valid.
            If not all mixing fractions are valid.
            If number of years, days, depths, and incorporation and mixing fractions are not equal.

        """
        error_header = f"'{self.name}': "

        valid_years = self._validate_years(self.years)
        if not valid_years:
            raise ValueError(
                error_header + f"expected all years to be > 0 and in non-descending order, received " f"'{self.years}'."
            )

        valid_days = self._validate_days(self.years, self.days)
        if not valid_days:
            raise ValueError(
                error_header + f"expected all planting days to be in range [1, 366], received " f"'{self.days}'."
            )

        valid_depths = self._validate_depths(self.tillage_depths)
        if not valid_depths:
            raise ValueError(
                error_header + f"expected all tillage depths to be > 0.0, received " f"'{self.tillage_depths}'."
            )

        valid_incorp_fractions = self._validate_fractions(self.incorporation_fractions)
        if not valid_incorp_fractions:
            raise ValueError(
                error_header + f"expected all incorporation fractions to be in range [0.0, 1.0], received "
                f"'{self.incorporation_fractions}'."
            )

        valid_mix_fractions = self._validate_fractions(self.mixing_fractions)
        if not valid_mix_fractions:
            raise ValueError(
                error_header + f"expected all mixing fractions to be in range [0.0, 1.0], received "
                f"'{self.mixing_fractions}'."
            )

        equal_tillage_parameters = (
            len(self.years)
            == len(self.days)
            == len(self.tillage_depths)
            == len(self.incorporation_fractions)
            == len(self.mixing_fractions)
            == len(self.implements)
        )
        if not equal_tillage_parameters:
            raise ValueError(
                error_header + f"expected number of years, days, depths, incorporation and mixing fractions to be "
                f"equal, received '{self.years}' years, '{self.days}' days,  '{self.tillage_depths}' tillage depths, "
                f"'{self.incorporation_fractions}' incorporation fractions, '{self.mixing_fractions}' mixing fractions "
                f"and '{[str(implement) for implement in self.implements]}' implements."
            )

    def generate_tillage_events(self) -> List[TillageEvent]:
        """
        Generates a list of all tillage events that will happen over the full course of this TillageSchedule.

        Returns
        -------
        List[TillageEvent]
            List of all tillage events that will happen over the course of this TillageSchedule.

        """
        all_tilling_years = self._repeat_pattern(self.years, self.pattern_skip, self.pattern_repeat)
        all_tilling_days = self.days * (self.pattern_repeat + 1)
        all_tillage_depths = self.tillage_depths * (self.pattern_repeat + 1)
        all_incorporation_fractions = self.incorporation_fractions * (self.pattern_repeat + 1)
        all_mixing_fractions = self.mixing_fractions * (self.pattern_repeat + 1)
        all_implements = self.implements * (self.pattern_repeat + 1)
        all_tillage_events = list(
            zip(
                all_tillage_depths,
                all_incorporation_fractions,
                all_mixing_fractions,
                all_implements,
                all_tilling_years,
                all_tilling_days,
            )
        )

        tillage_events = []
        for event in all_tillage_events:
            new_tillage_event = TillageEvent(
                tillage_depth=event[0],
                incorporation_fraction=event[1],
                mixing_fraction=event[2],
                implement=event[3],
                year=event[4],
                day=event[5],
            )
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
        return all(depth > 0.0 for depth in tillage_depths)

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
        return all(0.0 <= fraction <= 1.0 for fraction in fractions)

from typing import List, Any

from RUFAS.data_structures.events import TillageEvent
from RUFAS.data_structures.tillage_implements import TillageImplement
from RUFAS.biophysical.field.manager.schedule import Schedule
from RUFAS.util import Utility


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

        self.tillage_depths = Utility.elongate_list(tillage_depths, len(years))
        self.incorporation_fractions = Utility.elongate_list(incorporation_fractions, len(years))
        self.mixing_fractions = Utility.elongate_list(mixing_fractions, len(years))

        self.implements = [TillageImplement(implement) for implement in implements]
        self.implements = Utility.elongate_list(self.implements, len(years))

        self._validate_tillage_parameters()

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
        fraction_parameters: list[tuple[str, list[Any]] | None] = [
            ("incorporation fractions", self.incorporation_fractions),
            ("mixing fractions", self.mixing_fractions),
        ]

        self._validate_parameters([], fraction_parameters, self.years, self.days, self.name)
        valid_depths = self.validate_positive_values(self.tillage_depths)
        if not valid_depths:
            raise ValueError(
                error_header + f"expected all tillage depths to be > 0.0, received " f"'{self.tillage_depths}'."
            )

        self.validate_equal_lengths(
            error_header,
            years=self.years,
            days=self.days,
            tillage_depths=self.tillage_depths,
            incorporation_fractions=self.incorporation_fractions,
            mixing_fractions=self.mixing_fractions,
            implements=self.implements,
        )

    def generate_tillage_events(self) -> List[TillageEvent]:
        """
        Generates a list of all tillage events that will happen over the full course of this TillageSchedule.

        Returns
        -------
        List[TillageEvent]
            List of all tillage events that will happen over the course of this TillageSchedule.

        """
        return list(
            self.generate_events(
                self.years,
                self.days,
                [],
                [self.tillage_depths, self.incorporation_fractions, self.mixing_fractions, self.implements],
                TillageEvent,
                self.pattern_skip,
                self.pattern_repeat,
            )
        )

from typing import List, Any

from RUFAS.data_structures.events import FertilizerEvent
from RUFAS.biophysical.field.manager.schedule import Schedule
from RUFAS.util import Utility


class FertilizerSchedule(Schedule):
    """
    A Schedule child class that defines the timing and amounts of fertilizer application to a field. Inherits from the
    Schedule class to manage and validate a schedule for applying specific fertilizer mixes to a field, including the
    timing (years and days) and amounts (masses of nitrogen, phosphorus, and potassium) of each application.

    Parameters
    ----------
    name : str
        The name of the fertilizer application schedule.
    mix_names : List[str]
        The names of the specific fertilizer mixes included in the schedule.
    years : List[int]
        The years in which the fertilizer will be applied.
    days : List[int]
        The Julian days on which the fertilizer will be applied within the specified years.
    nitrogen_masses : List[float]
        The minimum masses of nitrogen to be applied in each fertilizer application (kg).
    phosphorus_masses : List[float]
        The minimum masses of phosphorus to be applied in each fertilizer application (kg).
    potassium_masses : List[float]
        The minimum masses of potassium to be applied in each fertilizer application (kg).
    application_depths : List[float], optional, default None
        The depths at which the fertilizer is to be injected into the soil for each application (mm).
    surface_remainder_fractions : List[float], optional, default None
        The fractions of each fertilizer application that remain on the soil surface (unitless).
    pattern_skip : int, optional, default 0.0
        The number of years to skip between repetitions of the fertilizer application pattern.
    pattern_repeat : int, optional, default 0.0
        The number of times the specified fertilizer application pattern should be repeated.

    Attributes
    ----------
    mix_names : List[str]
        Elongated list of mix names to match the length of the years list, ensuring a mix name for each application
        year.
    nitrogen_masses : List[float]
        Elongated list of nitrogen masses to match the length of the years list, ensuring a nitrogen mass for each
        application year.
    phosphorus_masses : List[float]
        Elongated list of phosphorus masses to match the length of the years list, ensuring a phosphorus mass for each
        application year.
    potassium_masses : List[float]
        Elongated list of potassium masses to match the length of the years list, ensuring a potassium mass for each
        application year.
    application_depths : List[float]
        Elongated list or default value [0.0] for application depths, ensuring an application depth for each application
        year.
    surface_remainder_fractions : List[float]
        Elongated list or default value [1.0] for surface remainder fractions, ensuring a fraction for each application
        year.

    Notes
    -----
    Application depths and surface remainder fractions are intended to have defaults of [0.0] and [1.0] respectively,
      but these are not specified directly in the function signature to avoid using mutable default arguments.

    """

    def __init__(
        self,
        name: str,
        mix_names: List[str],
        years: List[int],
        days: List[int],
        nitrogen_masses: List[float],
        phosphorus_masses: List[float],
        potassium_masses: List[float],
        application_depths: List[float] | None = None,
        surface_remainder_fractions: List[float] | None = None,
        pattern_skip: int = 0,
        pattern_repeat: int = 0,
    ):
        super().__init__(name, years, days, pattern_skip, pattern_repeat)

        self.mix_names = Utility.elongate_list(mix_names, len(years))
        self.nitrogen_masses = Utility.elongate_list(nitrogen_masses, len(years))
        self.phosphorus_masses = Utility.elongate_list(phosphorus_masses, len(years))
        self.potassium_masses = Utility.elongate_list(potassium_masses, len(years))

        if application_depths is None:
            application_depths = [0.0]
        self.application_depths = Utility.elongate_list(application_depths, len(years))

        if surface_remainder_fractions is None:
            surface_remainder_fractions = [1.0]
        self.surface_remainder_fractions = Utility.elongate_list(surface_remainder_fractions, len(years))

        self._validate_fertilizer_parameters()

    def _validate_fertilizer_parameters(self) -> None:
        """
        Checks that all fields defining a fertilizer application schedule are valid, raises errors if not.

        Raises
        ------
        ValueError
            If not all fertilizer application years are valid.
            If not all fertilizer application days are valid.
            If not all fertilizer nitrogen masses are valid.
            If not all fertilizer phosphorus masses are valid.
            If not all fertilizer potassium masses are valid.
            If not all fertilizer application depths are valid.
            If not all fertilizer surface retention fractions are valid.
            If not all fertilizer application parameters have the same length.

        """
        error_header = f"'{self.name}': "
        non_negative_parameters: list[tuple[str, list[Any]] | None] = [
            ("nitrogen masses", self.nitrogen_masses),
            ("phosphorus masses", self.phosphorus_masses),
            ("potassium masses", self.potassium_masses),
            ("application depths", self.application_depths),
        ]
        fraction_parameters: list[tuple[str, list[Any]] | None] = [
            ("surface remainder fractions", self.surface_remainder_fractions)
        ]

        self._validate_parameters(non_negative_parameters, fraction_parameters, self.years, self.days, self.name)

        self.validate_equal_lengths(
            error_header,
            years=self.years,
            days=self.days,
            mix_names=self.mix_names,
            nitrogen_masses=self.nitrogen_masses,
            phosphorus_masses=self.phosphorus_masses,
            potassium_masses=self.potassium_masses,
            application_depths=self.application_depths,
            surface_remainder_fractions=self.surface_remainder_fractions,
        )

    def generate_fertilizer_events(self) -> List[FertilizerEvent]:
        """
        Creates a list of all fertilizer application events that will occur as dictated by this fertilizer schedule.

        Returns
        -------
        List[FertilizerEvent]
            List of all fertilizer events that occur over the course of this fertilizer schedule.

        """
        return list(
            self.generate_events(
                self.years,
                self.days,
                [],
                [
                    self.mix_names,
                    self.nitrogen_masses,
                    self.phosphorus_masses,
                    self.potassium_masses,
                    self.application_depths,
                    self.surface_remainder_fractions,
                ],
                FertilizerEvent,
                self.pattern_skip,
                self.pattern_repeat,
            )
        )

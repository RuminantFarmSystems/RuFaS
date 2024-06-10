from typing import List, Any

from RUFAS.routines.field.manager.schedule import Schedule
from RUFAS.routines.field.manager.events import FertilizerEvent
from RUFAS.output_manager import OutputManager


om = OutputManager()


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
        application_depths: List[float] = None,
        surface_remainder_fractions: List[float] = None,
        pattern_skip: int = 0,
        pattern_repeat: int = 0,
    ):
        super().__init__(name, years, days, pattern_skip, pattern_repeat)

        self.mix_names = self._elongate_list(mix_names, len(years))
        self.nitrogen_masses = self._elongate_list(nitrogen_masses, len(years))
        self.phosphorus_masses = self._elongate_list(phosphorus_masses, len(years))
        self.potassium_masses = self._elongate_list(potassium_masses, len(years))

        if application_depths is None:
            application_depths = [0.0]
        self.application_depths = self._elongate_list(application_depths, len(years))

        if surface_remainder_fractions is None:
            surface_remainder_fractions = [1.0]
        self.surface_remainder_fractions = self._elongate_list(surface_remainder_fractions, len(years))

        self._validate_fertilizer_parameters()

        self._validate_pattern_parameters()

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

        valid_years = self._validate_years(self.years)
        if not valid_years:
            raise ValueError(
                error_header + f"expected all years to be > 0 and in non-descending order, received " f"'{self.years}'."
            )

        valid_days = self._validate_days(self.years, self.days)
        if not valid_days:
            raise ValueError(error_header + f"expected all days to be in range [1, 366], received '{self.days}'.")

        valid_nitrogen_masses = self._determine_if_all_non_negative_values(self.nitrogen_masses)
        if not valid_nitrogen_masses:
            raise ValueError(
                error_header + f"expected all nitrogen masses to be in >= 0, received " f"'{self.nitrogen_masses}'."
            )

        valid_phosphorus_masses = self._determine_if_all_non_negative_values(self.phosphorus_masses)
        if not valid_phosphorus_masses:
            raise ValueError(
                error_header + f"expected all phosphorus masses to be >= 0, received " f"'{self.phosphorus_masses}'."
            )

        valid_potassium_masses = self._determine_if_all_non_negative_values(self.potassium_masses)
        if not valid_potassium_masses:
            raise ValueError(
                error_header + f"expected all potassium masses to be >= 0, received '{self.potassium_masses}'."
            )

        valid_depths = self._determine_if_all_non_negative_values(self.application_depths)
        if not valid_depths:
            raise ValueError(
                error_header + f"expected all application depths to be >= 0, received " f"'{self.application_depths}'."
            )

        valid_fractions = all(0.0 <= fraction <= 1.0 for fraction in self.surface_remainder_fractions)
        if not valid_fractions:
            raise ValueError(
                error_header + f"expected all surface remainder fractions to be in range [0.0, 1.0], "
                f"received '{self.surface_remainder_fractions}'."
            )

        equal_fertilizer_parameters = (
            len(self.years)
            == len(self.days)
            == len(self.mix_names)
            == len(self.nitrogen_masses)
            == len(self.phosphorus_masses)
            == len(self.potassium_masses)
            == len(self.application_depths)
            == len(self.surface_remainder_fractions)
        )
        if not equal_fertilizer_parameters:
            raise ValueError(
                error_header + f"expected equal numbers of fertilizer application parameters, received "
                f"'{self.years}' years, '{self.days}' days, '{self.mix_names}' mix names, "
                f"'{self.nitrogen_masses}' nitrogen masses, '{self.phosphorus_masses}' "
                f"phosphorus masses, '{self.potassium_masses}' potassium masses, '{self.application_depths}' "
                "application depths, and '{self.surface_remainder_fractions}' surface remainder fractions."
            )

    def generate_fertilizer_events(self) -> List[FertilizerEvent]:
        """
        Creates a list of all fertilizer application events that will occur as dictated by this fertilizer schedule.

        Returns
        -------
        List[FertilizerEvent]
            List of all fertilizer events that occur over the course of this fertilizer schedule.

        """
        all_years = self._repeat_pattern(self.years, self.pattern_skip, self.pattern_repeat)
        all_days = self.days * (self.pattern_repeat + 1)
        all_mix_names = self.mix_names * (self.pattern_repeat + 1)
        all_nitrogen_masses = self.nitrogen_masses * (self.pattern_repeat + 1)
        all_phosphorus_masses = self.phosphorus_masses * (self.pattern_repeat + 1)
        all_potassium_masses = self.potassium_masses * (self.pattern_repeat + 1)
        all_depths = self.application_depths * (self.pattern_repeat + 1)
        all_surface_fractions = self.surface_remainder_fractions * (self.pattern_repeat + 1)
        all_events = list(
            zip(
                all_mix_names,
                all_years,
                all_days,
                all_nitrogen_masses,
                all_phosphorus_masses,
                all_potassium_masses,
                all_depths,
                all_surface_fractions,
            )
        )

        fertilizer_events = []
        for event in all_events:
            new_event = FertilizerEvent(
                mix_name=event[0],
                year=event[1],
                day=event[2],
                nitrogen_mass=event[3],
                phosphorus_mass=event[4],
                potassium_mass=event[5],
                depth=event[6],
                surface_remainder_fraction=event[7],
            )
            fertilizer_events.append(new_event)
        return fertilizer_events

    @staticmethod
    def _determine_if_all_non_negative_values(values: List[Any]) -> bool:
        """
        Checks that all values in a list are >= 0.

        Parameters
        ----------
        values : List[Any]
            List of values to be checked.

        Returns
        -------
        bool
            True if all values are >= 0, False otherwise.

        """
        return all(value >= 0 for value in values)

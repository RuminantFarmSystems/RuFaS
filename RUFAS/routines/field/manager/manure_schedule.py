from typing import List, Optional

from RUFAS.data_structures.events import ManureEvent
from RUFAS.routines.field.manager.schedule import Schedule
from RUFAS.data_structures.manure_types import ManureType
from RUFAS.util import Utility


class ManureSchedule(Schedule):
    """
    A Schedule child class that defines when and how much manure will be applied to a field.

    Parameters
    ----------
    name : str
        The name of the manure application schedule.
    years : List[int]
        The years in which the manure will be applied.
    days : List[int]
        The Julian days on which the manure will be applied within the specified years.
    nitrogen_masses : List[float]
        The minimum masses of nitrogen to be applied in each manure application (kg).
    phosphorus_masses : List[float]
        The minimum masses of phosphorus to be applied in each manure application (kg).
    manure_types : List[ManureType]
        The types of manure to be applied.
    field_coverages : List[float]
        The fractions of the field covered by manure applications (unitless).
    application_depths : List[float], optional
        The depths at which the manure is to be injected into the soil for each application (mm).
    surface_remainder_fractions : List[float], optional
        The fractions of each manure application that remain on the soil surface (unitless).
    pattern_skip : int, optional
        The number of years to skip between repetitions of the manure application pattern.
    pattern_repeat : int, optional
        The number of times the specified manure application pattern should be repeated.

    Attributes
    ----------
    nitrogen_masses : List[float]
        Elongated list of nitrogen masses to ensure a mass value for each application year.
    phosphorus_masses : List[float]
        Elongated list of phosphorus masses to ensure a mass value for each application year.
    manure_types : List[ManureType]
        Elongated list of manure types to ensure a type for each application year.
    field_coverages : List[float]
        Elongated list of field coverages to ensure a coverage value for each application year.
    application_depths : List[float]
        Elongated list or default value for application depths to ensure a depth for each application year.
    surface_remainder_fractions : List[float]
        Elongated list or default value for surface remainder fractions to ensure a fraction for each application year.

    Notes
    -----
    Inherits from the Schedule class to manage and validate a schedule for applying specific manure types to a field,
    including the timing (years and days) and amounts (masses of nitrogen and phosphorus) of each application.

    """

    def __init__(
        self,
        name: str,
        years: List[int],
        days: List[int],
        nitrogen_masses: List[float],
        phosphorus_masses: List[float],
        manure_types: List[ManureType],
        field_coverages: List[float],
        application_depths: Optional[List[float]] = None,
        surface_remainder_fractions: Optional[List[float]] = None,
        pattern_skip: int = 0,
        pattern_repeat: int = 0,
    ):
        super().__init__(name, years, days, pattern_skip, pattern_repeat)

        self.nitrogen_masses = Utility.elongate_list(nitrogen_masses, len(years))
        self.phosphorus_masses = Utility.elongate_list(phosphorus_masses, len(years))
        self.manure_types = Utility.elongate_list(manure_types, len(years))
        self.field_coverages = Utility.elongate_list(field_coverages, len(years))

        if application_depths is None:
            application_depths = [0.0]
        self.application_depths = Utility.elongate_list(application_depths, len(years))

        if surface_remainder_fractions is None:
            surface_remainder_fractions = [1.0]
        self.surface_remainder_fractions = Utility.elongate_list(surface_remainder_fractions, len(years))

        self._validate_manure_parameters()

    def _validate_manure_parameters(self) -> None:
        """
        Checks that all parameters defining manure application schedule are valid, otherwise raises error.

        Raises
        ------
        ValueError
            If not all manure application years are valid.
            If not all manure application days are valid.
            If not all manure nitrogen masses are valid.
            If not all manure phosphorus masses are valid.
            If not all manure types are valid.
            If not all field coverage fractions are valid.
            If not all manure application depths are valid.
            If not all manure surface retention fractions are valid.
            If not all manure application parameters have the same length.

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

        valid_nitrogen_masses = Utility.determine_if_all_non_negative_values(self.nitrogen_masses)
        if not valid_nitrogen_masses:
            raise ValueError(
                error_header + f"expected all nitrogen masses to be >= 0, received " f"'{self.nitrogen_masses}'."
            )

        valid_phosphorus_masses = Utility.determine_if_all_non_negative_values(self.phosphorus_masses)
        if not valid_phosphorus_masses:
            raise ValueError(
                error_header + f"expected all phosphorus masses to be >= 0, received " f"'{self.phosphorus_masses}'."
            )

        valid_manure_types = all(isinstance(manure_type, ManureType) for manure_type in self.manure_types)
        if not valid_manure_types:
            raise ValueError(
                error_header + f"expected all manure types to be valid ManureTypes, received " f"'{self.manure_types}'."
            )

        valid_coverage_fractions = Utility.validate_fractions(self.field_coverages)
        if not valid_coverage_fractions:
            raise ValueError(
                error_header + f"expected all field coverage fractions to be in the range [0.0, 1.0], "
                f"received '{self.field_coverages}'."
            )

        valid_depths = Utility.determine_if_all_non_negative_values(self.application_depths)
        if not valid_depths:
            raise ValueError(
                error_header + f"expected all manure application depths to be >= 0, received "
                f"'{self.application_depths}'."
            )

        valid_surface_fractions = Utility.validate_fractions(self.surface_remainder_fractions)
        if not valid_surface_fractions:
            raise ValueError(
                error_header + f"expected all surface remainder fractions to be in the range [0.0, 1.0], "
                f"received '{self.surface_remainder_fractions}'."
            )

        self.validate_equal_lengths(
            error_header,
            years=self.years,
            days=self.days,
            nitrogen_masses=self.nitrogen_masses,
            phosphorus_masses=self.phosphorus_masses,
            application_depths=self.application_depths,
            surface_remainder_fractions=self.surface_remainder_fractions,
            manure_types=self.manure_types,
        )

    def generate_manure_events(self) -> List[ManureEvent]:
        """
        Creates a list of all manure applications that will be applied as dictated by this manure schedule.

        Returns
        -------
        List[ManureEvent]
            List of ManureEvents representing all manure applications that will occur over the simulation run.

        """
        all_years = Utility.repeat_pattern(self.years, self.pattern_skip, self.pattern_repeat)
        all_days = self.days * (self.pattern_repeat + 1)
        all_nitrogen_masses = self.nitrogen_masses * (self.pattern_repeat + 1)
        all_phosphorus_masses = self.phosphorus_masses * (self.pattern_repeat + 1)
        all_manure_types = self.manure_types * (self.pattern_repeat + 1)
        all_field_coverages = self.field_coverages * (self.pattern_repeat + 1)
        all_application_depths = self.application_depths * (self.pattern_repeat + 1)
        all_surface_remainder_fractions = self.surface_remainder_fractions * (self.pattern_repeat + 1)
        all_manure_application_events = list(
            zip(
                all_years,
                all_days,
                all_nitrogen_masses,
                all_phosphorus_masses,
                all_manure_types,
                all_field_coverages,
                all_application_depths,
                all_surface_remainder_fractions,
            )
        )

        manure_application_events = []
        for event in all_manure_application_events:
            new_event = ManureEvent(
                year=event[0],
                day=event[1],
                nitrogen_mass=event[2],
                phosphorus_mass=event[3],
                manure_type=event[4],
                field_coverage=event[5],
                application_depth=event[6],
                surface_remainder_fraction=event[7],
            )
            manure_application_events.append(new_event)
        return manure_application_events

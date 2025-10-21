from typing import List, Optional, Any

from RUFAS.data_structures.events import ManureEvent
from RUFAS.data_structures.manure_supplement_methods import ManureSupplementMethod
from RUFAS.biophysical.field.manager.schedule import Schedule
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
    manure_supplement_methods: list[ManureSupplementMethod]
        The methods that each event will use to supplement nutrient deficiencies.

    Attributes
    ----------
    nitrogen_masses : List[float]
        Elongated list of nitrogen masses to ensure a mass value for each application year.
    phosphorus_masses : list[float]
        Elongated list of phosphorus masses to ensure a mass value for each application year.
    manure_types : list[ManureType]
        Elongated list of manure types to ensure a type for each application year.
    field_coverages : list[float]
        Elongated list of field coverages to ensure a coverage value for each application year.
    application_depths : list[float]
        Elongated list or default value for application depths to ensure a depth for each application year.
    surface_remainder_fractions : list[float]
        Elongated list or default value for surface remainder fractions to ensure a fraction for each application year.
    manure_supplement_methods: list[ManureSupplementMethod]
        The methods that each event will use to supplement nutrient deficiencies.

    Notes
    -----
    Inherits from the Schedule class to manage and validate a schedule for applying specific manure types to a field,
    including the timing (years and days) and amounts (masses of nitrogen and phosphorus) of each application.

    """

    def __init__(
        self,
        name: str,
        years: list[int],
        days: list[int],
        nitrogen_masses: list[float],
        phosphorus_masses: list[float],
        manure_types: list[ManureType],
        manure_supplement_methods: list[ManureSupplementMethod],
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
        self.manure_supplement_methods = Utility.elongate_list(manure_supplement_methods, len(years))
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
        non_negative_parameters: list[tuple[str, list[Any]] | None] = [
            ("nitrogen masses", self.nitrogen_masses),
            ("phosphorus masses", self.phosphorus_masses),
            ("manure application depths", self.application_depths),
        ]
        fraction_parameters: list[tuple[str, list[Any]] | None] = [
            ("field coverages", self.field_coverages),
            ("surface remainder fractions", self.surface_remainder_fractions),
        ]

        self._validate_parameters(non_negative_parameters, fraction_parameters, self.years, self.days, self.name)
        valid_manure_types = all(isinstance(manure_type, ManureType) for manure_type in self.manure_types)
        if not valid_manure_types:
            raise ValueError(
                error_header + f"expected all manure types to be valid ManureTypes, received " f"'{self.manure_types}'."
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
            manure_supplement_methods=self.manure_supplement_methods,
        )

    def generate_manure_events(self) -> list[ManureEvent]:
        """
        Creates a list of all manure applications that will be applied as dictated by this manure schedule.

        Returns
        -------
        list[ManureEvent]
            List of ManureEvents representing all manure applications that will occur over the simulation run.

        """
        return list(
            self.generate_events(
                self.years,
                self.days,
                [],
                [
                    self.nitrogen_masses,
                    self.phosphorus_masses,
                    self.manure_types,
                    self.manure_supplement_methods,
                    self.field_coverages,
                    self.application_depths,
                    self.surface_remainder_fractions,
                ],
                ManureEvent,
                self.pattern_skip,
                self.pattern_repeat,
            )
        )

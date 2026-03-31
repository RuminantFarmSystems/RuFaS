"""This module defines the various BaseFieldManagementEvent classes and helper functions

Events are simple classes that will facilitate scheduling of different management operations. At their core, they
are simply pairs of attributes (`year` and `day`), indicating when particular operations should occur. Children of
the main `BaseFieldManagementEvent` class can extend the functionality by adding additional attributes specific to the
type of management operation. For example, the `HarvestEvent` contains the `operation` attribute, which specifies which
specific harvest method will be used when harvesting a crop, and a `crop_reference` attribute, which specifies which
crop that is presently growing in a field will be harvested.
"""

from datetime import date

from RUFAS.data_structures.manure_supplement_methods import ManureSupplementMethod
from RUFAS.data_structures.manure_types import ManureType
from RUFAS.data_structures.tillage_implements import TillageImplement
from RUFAS.biophysical.field.crop.harvest_operations import HarvestOperation
from RUFAS.rufas_time import RufasTime


class BaseFieldManagementEvent:
    """
    Class that will facilitate scheduling of different management operations.

    Parameters
    ----------
    year : int, default 1
        Year of the simulation on which the event should occur.
    day : int, default 120
        Julian day of the year on which the event should occur.

    Attributes
    ----------
    year : int
        Year of the simulation on which the event should occur.
    day : int
        Julian day of the year on which the event should occur.

    Notes
    -----
    An event can specify when a crop is planted or harvested, when a manure/fertilizer amendment should occur.

    """

    def __init__(self, year: int = 1, day: int = 120):
        self.year = year
        self.day = day

    def __eq__(self, other) -> bool:
        """Overrides the equality operator for BaseFieldManagementEvent objects."""
        if isinstance(other, BaseFieldManagementEvent):
            return other.year == self.year and other.day == self.day
        return False

    def __hash__(self) -> int:
        """Overrides the hash method for BaseFieldManagementEvent objects."""
        return hash((self.year, self.day))

    def occurs_today(self, time: RufasTime) -> bool:
        """
        Checks if the event occurs on the current day in the current year..

        Parameters
        ----------
        time : RufasTime
            RufasTime object that contains the current day and year.

        Returns
        -------
        bool
            True if event occurs on the current day and year, false if not.

        """
        return self.year == time.current_calendar_year and self.day == time.current_julian_day

    @property
    def date_occurs(self) -> date:
        """Gets the date when the event occurs."""
        return RufasTime.convert_year_jday_to_date(self.year, self.day).date()


class PlantingEvent(BaseFieldManagementEvent):
    """
    A child of BaseFieldManagementEvent class that dictates when a crop will be planted and how it will eventually be
    harvested.

    Parameters
    ----------
    crop_reference : str
        Name of the crop to be planted in the ground.
    heat_scheduled_harvest : bool, default=False
        Flag indicating if the crop will be harvested when it has a certain amount of heat units.

    """

    def __init__(
        self, crop_reference: str, heat_scheduled_harvest: bool = False, year: int = 1, day: int = 120
    ) -> None:
        super().__init__(year=year, day=day)
        self.crop_reference = crop_reference
        self.use_heat_scheduled_harvest = heat_scheduled_harvest

    def __eq__(self, other) -> bool:
        """Overrides the equality operator for PlantingEvent objects."""
        if isinstance(other, PlantingEvent):
            return (
                super().__eq__(other)
                and other.crop_reference == self.crop_reference
                and other.use_heat_scheduled_harvest == self.use_heat_scheduled_harvest
            )
        return False

    def __hash__(self) -> int:
        """Overrides the hash method for PlantingEvent objects."""
        return hash((self.crop_reference, self.year, self.day, self.use_heat_scheduled_harvest))


class HarvestEvent(BaseFieldManagementEvent):
    """
    A child of BaseFieldManagementEvent class that determines when (and how) a harvest operation should occur for a
    crop.

    Parameters
    ----------
    crop_reference : str
        Name of the crop to be harvested.
    operation : HarvestOperation, default=HarvestOperation.HARVEST_KILL
        A harvest operation from the Harvest Operations enum.

    """

    def __init__(
        self,
        crop_reference: str,
        operation: HarvestOperation = HarvestOperation.HARVEST_KILL,
        year: int = 1,
        day: int = 240,
    ):
        super().__init__(year=year, day=day)
        self.crop_reference = crop_reference
        self.operation = operation

    def __eq__(self, other) -> bool:
        """Overrides the equality operator for HarvestEvent objects."""
        if isinstance(other, HarvestEvent):
            return (
                super().__eq__(other)
                and other.crop_reference == self.crop_reference
                and other.operation == self.operation
            )
        return False

    def __hash__(self) -> int:
        """Overrides the hash method for HarvestEvent objects."""
        return hash((self.year, self.day, self.crop_reference, self.operation))


class TillageEvent(BaseFieldManagementEvent):
    """
    A child of BaseFieldManagementEvent class that defines a tillage application to be applied on a specific day of a
    year.

    Parameters
    ----------
    tillage_depth : float
        The lowest depth the tilling implement reaches (mm).
    incorporation_fraction : float
        Fraction of soil surface pool incorporated into the soil profile (unitless).
    mixing_fraction : float
        Fraction of pool in each layer mixed and redistributed back into the soil profile (unitless).
    implement : TillageImplement
        Tillage implement that is being used to execute this tillage application.

    """

    def __init__(
        self,
        tillage_depth: float,
        incorporation_fraction: float,
        mixing_fraction: float,
        implement: TillageImplement,
        year: int = 1,
        day: int = 160,
    ):
        super().__init__(year=year, day=day)
        self.tillage_depth = tillage_depth
        self.incorporation_fraction = incorporation_fraction
        self.mixing_fraction = mixing_fraction
        self.implement = implement

    def __eq__(self, other) -> bool:
        """Overrides the equality operator for TillageEvent objects."""
        if isinstance(other, TillageEvent):
            return (
                super().__eq__(other)
                and other.tillage_depth == self.tillage_depth
                and other.incorporation_fraction == self.incorporation_fraction
                and other.mixing_fraction == self.mixing_fraction
                and other.implement == self.implement
            )
        return False

    def __hash__(self) -> int:
        """Overrides the hash method for TillageEvent objects."""
        return hash(
            (self.year, self.day, self.tillage_depth, self.incorporation_fraction, self.mixing_fraction, self.implement)
        )


class ManureEvent(BaseFieldManagementEvent):
    """
    A child of BaseFieldManagementEvent class that defines how manure much manure such be requested and applied to a
    field.

    Parameters
    ----------
    year : int
        Year in which this manure application occurs.
    day : int
        Day in which this manure application occurs.
    nitrogen_mass : float
        Minimum mass of nitrogen that should be contained in this manure application (kg).
    phosphorus_mass : float
        Minimum mass of phosphorus that should be contained in this manure application (kg).
    manure_type : ManureType
        The type of manure for which the application request will be made.
    manure_supplement_method : ManureSupplementMethod
        The method that the event will use to supplement nutrient deficiencies.
    field_coverage : float
        Fraction of the field covered by this manure application (unitless).
    application_depth : float
        Depth that manure is injected into the soil at (mm).
    surface_remainder_fraction : float
        Fraction of manure applied that remains on the soil surface (unitless).

    """

    def __init__(
        self,
        nitrogen_mass: float,
        phosphorus_mass: float,
        manure_type: ManureType,
        manure_supplement_method: ManureSupplementMethod,
        field_coverage: float,
        application_depth: float,
        surface_remainder_fraction: float,
        year: int,
        day: int,
    ):
        super().__init__(year=year, day=day)
        self.nitrogen_mass = nitrogen_mass
        self.phosphorus_mass = phosphorus_mass
        self.manure_type = manure_type
        self.manure_supplement_method = manure_supplement_method
        self.field_coverage = field_coverage
        self.application_depth = application_depth
        self.surface_remainder_fraction = surface_remainder_fraction

    def __eq__(self, other) -> bool:
        """Overrides the equality operator for ManureEvent objects."""
        if isinstance(other, ManureEvent):
            return (
                super().__eq__(other)
                and other.nitrogen_mass == self.nitrogen_mass
                and other.phosphorus_mass == self.phosphorus_mass
                and other.manure_type == self.manure_type
                and other.field_coverage == self.field_coverage
                and other.application_depth == self.application_depth
                and other.surface_remainder_fraction == self.surface_remainder_fraction
                and other.manure_supplement_method == self.manure_supplement_method
            )
        return False

    def __hash__(self) -> int:
        """Overrides the hash method for ManureEvent objects."""
        return hash(
            (
                self.year,
                self.day,
                self.nitrogen_mass,
                self.phosphorus_mass,
                self.manure_type,
                self.field_coverage,
                self.application_depth,
                self.surface_remainder_fraction,
            )
        )


class FertilizerEvent(BaseFieldManagementEvent):
    """
    A child of BaseFieldManagementEvent class that defines the parameters of a single fertilizer application.

    Parameters
    ----------
    mix_name : str
        Name of the fertilizer mix being used.
    year : int
        Year in which this application occurs.
    day : int
        Day on which this application occurs.
    nitrogen_mass : float
        Minimum mass of nitrogen that should be in this application (kg).
    phosphorus_mass : float
        Minimum mass of phosphorus that should be in this application (kg).
    potassium_mass : float
        Minimum mass of potassium that should be in this application (kg).
    depth : float
        Depth at which fertilizer is injected into the soil.
    surface_remainder_fraction : float
        Fraction of fertilizer that remains on the soil surface after application.
    """

    def __init__(
        self,
        mix_name: str,
        nitrogen_mass: float,
        phosphorus_mass: float,
        potassium_mass: float,
        depth: float,
        surface_remainder_fraction: float,
        year: int,
        day: int,
    ):
        super().__init__(year=year, day=day)
        self.mix_name = mix_name
        self.nitrogen_mass = nitrogen_mass
        self.phosphorus_mass = phosphorus_mass
        self.potassium_mass = potassium_mass
        self.depth = depth
        self.surface_remainder_fraction = surface_remainder_fraction

    def __eq__(self, other) -> bool:
        """Overrides the equality operator for FertilizerEvent objects."""
        if isinstance(other, FertilizerEvent):
            return (
                super().__eq__(other)
                and other.mix_name == self.mix_name
                and other.nitrogen_mass == self.nitrogen_mass
                and other.phosphorus_mass == self.phosphorus_mass
                and other.potassium_mass == self.potassium_mass
                and other.depth == self.depth
                and other.surface_remainder_fraction == self.surface_remainder_fraction
            )
        return False

    def __hash__(self) -> int:
        """Overrides the hash method for FertilizerEvent objects."""
        return hash(
            (
                self.year,
                self.day,
                self.mix_name,
                self.nitrogen_mass,
                self.phosphorus_mass,
                self.potassium_mass,
                self.depth,
                self.surface_remainder_fraction,
            )
        )
